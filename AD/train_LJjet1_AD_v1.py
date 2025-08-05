'''
    Author: J Curran
    Description: example script for AD based training / testing 
        Run: setupATLAS OR 
             export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
             source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh 
             Then TRY LCG REL: 
             lsetup "views LCG_107_swan x86_64-el9-gcc13-opt"
             python3 train_LJjet1_AD_v1.py 
'''

import uproot
from ROOT import TFile, TTree, TObject
import numpy as np
import tensorflow as tf
from keras import backend as K
from tensorflow.keras.layers import Dense, Input, LeakyReLU
from tensorflow.keras import Model
from matplotlib import pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from array import array
import time

class SimpleAE: 

    def __init__(self, all_sig_filepaths, sig_filepath, bgd_filepath, tree_name):
        self.sig_filepath = sig_filepath 
        self.bgd_filepath = bgd_filepath
        self.tree_name    = tree_name
        self.all_sig_filepaths = all_sig_filepaths

    def data_prep(self, filepath):
        """
        Open the root file and return an array of variables to train AE
        """
        f=uproot.open(filepath)
        tree = f[self.tree_name]

        #convert branches to arrays 
        evnt_number   = tree.arrays("eventNumber")["eventNumber"]
        LJjet1_m      = tree.arrays("LJjet1_m")["LJjet1_m"]   
        LJjet1_jvt    = tree.arrays("LJjet1_jvt")["LJjet1_jvt"]      
        LJjet1_width  = tree.arrays("LJjet1_width")["LJjet1_width"]     
        LJjet1_EMfrac = tree.arrays("LJjet1_EMfrac")["LJjet1_EMfrac"]

        evnt_number   = np.array(evnt_number).reshape(len(evnt_number), 1)
        LJjet1_m      = np.array(LJjet1_m).reshape(len(LJjet1_m), 1)
        LJjet1_jvt    = np.array(LJjet1_jvt).reshape(len(LJjet1_jvt), 1)
        LJjet1_width  = np.array(LJjet1_width).reshape(len(LJjet1_width), 1)
        LJjet1_EMfrac = np.array(LJjet1_EMfrac).reshape(len(LJjet1_EMfrac), 1)

        # track events for mse score - eventNumber's repeated 
        track_ev = np.linspace(0, len(evnt_number)-1, num=len(evnt_number))
        track_evnts   = np.array(track_ev).reshape(len(track_ev), 1)

        array_forAD = np.hstack((LJjet1_m, LJjet1_jvt, LJjet1_width, LJjet1_EMfrac)) 

        print("Loaded data")
        return evnt_number, array_forAD, np.array(track_evnts)

    def normalise(self, file_tonorm): 
        """
        Normalisation of training / testing inputs to pass through AE - for basic normalisation need to pass all signals + backgrounds 
        """       
        # Signal file or Background to normalise 
        evnt_num, arrToNorm, track_evnts = self.data_prep(file_tonorm)

        # Load all signal / background data to ensure same normalisation for Bkgs and signals 
        evnt_num_bkg, bkg_array, track_evnts_bkg = self.data_prep(self.bgd_filepath)

        sig_arrays = []
        for sig_filepath in self.all_sig_filepaths:
            evnt_num_sig, sig_array, track_evnts_sig = self.data_prep(sig_filepath)
            print(sig_array)
            sig_arrays.append(sig_array)
            print(sig_array.shape)
        print(bkg_array.shape)
       
        # Stack signals and Bakgrounds 
        combined_array = np.vstack([bkg_array] + sig_arrays)

        #Fit and transform data 
        scaler = StandardScaler()
        fitted_scaler = scaler.fit(combined_array)
        normalised_data = fitted_scaler.transform(arrToNorm)

        return evnt_num, normalised_data, track_evnts

    def data_prep_train_test(self, file_tonorm):
        """
        Normalise inputs and Define training and testing datasets
        """
        # Get normalised data - store evnt nums used in training/testing 
        evnt_nums, normed_data, track_evnts_data = self.normalise(file_tonorm)
        norm_input_data = np.hstack([track_evnts_data, normed_data])
        train_LJjet1, test_LJjet1 = train_test_split(norm_input_data,random_state=64,test_size=.2, shuffle=True)
        return train_LJjet1, test_LJjet1, track_evnts_data

    def model_AE(self, input_shape, encoding_dim, hidden_nodes=None):
        """
        Define the AE model 
        """
        #Inputs
        inputArray = Input(shape=(input_shape,))
        x  = Dense(4, activation=tf.nn.leaky_relu)(inputArray)
        if hidden_nodes: 
            x  = Dense(hidden_nodes, activation=tf.nn.leaky_relu)(x)
        #Encoder 
        enc = Dense(encoding_dim, activation=tf.nn.leaky_relu)(x)
        #Decoder
        if hidden_nodes: 
            x  = Dense(4, activation=tf.nn.leaky_relu)(enc)
            dec = Dense(input_shape, activation = 'linear')(x) # [-, +]
        else: 
            dec = Dense(input_shape, activation = 'linear')(enc) # [-, +]

        #create autoencoder
        autoencoder = Model(inputs = inputArray, outputs=dec, name = 'AutoEncoder')
        #compile model 
        autoencoder.compile('adam', loss='mean_squared_error',metrics=['mse'])
        return autoencoder

    #determine an average mse value for the pts 
    def mse_loss_pt(self, true, prediction):
        loss = tf.reduce_mean(tf.math.square(true - prediction),axis=-1)
        return loss

    def train(self, enc_dim, epochs_, batch_size_):
        """
        Train the AE
        """
        #train / test split for backgrounds 
        training_data, testing_data, evnt_nums = self.data_prep_train_test(self.bgd_filepath)
        #remove evnt number 
        trimmed_training_data = training_data[:, 1:]
        trimmed_testing_data  = testing_data[:, 1:]
        inp_dim = trimmed_training_data.shape[1]
        print(f"Input dimensions for training : {trimmed_training_data.shape[0], trimmed_training_data.shape[1]}")
    
        if enc_dim >= inp_dim:
            raise Exception("Need data compression")
        # instantiate model + print summary  
        BasicAE = self.model_AE(input_shape=inp_dim, encoding_dim=enc_dim)
        
        #print summary model
        BasicAE.summary()

        # training 
        history = BasicAE.fit(trimmed_training_data, trimmed_training_data, epochs=epochs_, validation_split=0.2, batch_size=batch_size_, verbose = 1)

        # Test on Background sub-set
        print("Reconstruction on testing data")
        recon_test_data = BasicAE.predict(trimmed_testing_data)
        mse_test_data   = self.mse_loss_pt(trimmed_testing_data, recon_test_data)

        return history, BasicAE, recon_test_data, mse_test_data, training_data, testing_data, evnt_nums

    def mse_signals(self, trained_model):
        """
        Evaluate the mse score for the signal sample
        """
        mse_scores = []
        for signal in self.all_sig_filepaths:
            # Get normalised signals data - store evnt nums used in training/testing 
            evnt_nums, normed_data, track_evnts = self.normalise(signal)
            #predict on signal 
            recon_signals = trained_model.predict(normed_data)
            #MSE score 
            mse_signals   = self.mse_loss_pt(normed_data, recon_signals)
            mse_scores.append(mse_signals)
        return mse_scores

    def plot_loss(self, loss, val_loss, scale, name = None, save=False, ylim = False):
        """
        Plot the loss during training of the AE 
        """
        fig, ax = plt.subplots(1, figsize=(8, 6), dpi=100)

        if (scale == 'log'):
            ax.set_yscale('log')
            
        ax.plot(loss, color = 'b', label = 'loss')
        ax.plot(val_loss, color = 'orange',  label = 'val loss')
        ax.set_title('Loss across training epochs')
        ax.set_xlim(left=-1)
        if ylim: ax.set_ylim(0,ylim)
        ax.set_xlabel('Epochs')
        ax.set_ylabel('Loss Value')
        ax.legend(bbox_to_anchor=(0.6, 1.03), loc="upper left")
        plt.show()
        if save : fig.savefig(f"Loss_{name}.pdf", bbox_inches='tight', dpi=150)
        return print("Plotted Loss")
    
      
    def get_bins(scores, bins_size, scaled01):
    
        if len(scores) > 1:
            join_scores = np.concatenate(scores, axis=0)
        else: 
            join_scores = scores[0]
        if scaled01:
            bins_all = round(1.0/bins_size)
            bins_min, bins_max = 0, 1
        else: 
            bins_all = round((np.max(join_scores) - np.min(join_scores)) / bins_size)
            bins_min, bins_max = np.min(join_scores), np.max(join_scores)
        
        return bins_all,[bins_min, bins_max]
    
    
    def plot_mse(self, inp_scores, bins_size, scale, labels, colours, name=None, xlim=None, save=False):
        """
        Plot the mse score of testing bkg vs signal
        """

        scores = [in_tensor.numpy() for in_tensor in inp_scores]
        ##get range of data and bsm for bin counts 
        mse_data = scores[0]
        mse_bsm  = np.concatenate(scores[1:])
        min_bin  = min(np.min(mse_data), np.min(mse_bsm))
        max_bin  = min(np.max(mse_data), np.max(mse_bsm))

        ranges  = [min_bin, max_bin]
        binvals = round((max_bin - min_bin) / bins_size)
    
        fig, ax = plt.subplots(1, figsize=(15, 10), dpi=100)

        #Plot Bkgs
        counts_data, bins_data, _ = ax.hist(scores[0], bins=binvals, label=labels[0], histtype='step', fill=False, linewidth=1.5, range=(ranges[0], ranges[1]), color='k')
        
        for i, label in enumerate(labels):
            if i==0: 
                continue
            else:
                ax.hist(scores[i], bins=binvals, label=label, histtype='step', fill=False, linewidth=1.5, range=(ranges[0], ranges[1]), color=colours[i], alpha=0.7)

        ax.set_ylabel( f"Events ", fontsize=20)
        ax.legend(bbox_to_anchor=(0.65, 1.), loc="upper left", fontsize=15, ncol=2)
        ax.set_xlabel('Anomaly score', fontsize=20)
        if xlim: ax.set_xlim(right=xlim)
        if (scale == 'log'): ax.set_yscale('log')
        ax.xaxis.get_offset_text().set_y(-1)

        if save: fig.savefig(f"Anomaly_Score_{name}.pdf", bbox_inches='tight', dpi=150)
        return plt.show()


    def add_Branch_Bkg(self, evnt_nums, evnt_nums_train, evnt_nums_test, mse_score_test, output_name):
        """
        Create a new root file from the bkg file that contains a tag for: 
        train_test_tag = 0 if training dataset, 1 if testing 
        mse_scores = -999 if training, actual mse score if testing 
        """
        print(f"Creating Root File : {output_name}")
        evnt_numbers   = evnt_nums
        print("Starting indexing ")
        start1 = time.time()
        indices_training = (evnt_nums_train).astype(int)
        indices_testing  = (evnt_nums_test).astype(int)
        
        # combine train / test limits 
        mse_combined = np.zeros((len(evnt_numbers),))
        
        # Set score for training data to -999 (shouldn't be used)
        mse_combined[[indices_training]] = -999
        for i, num in enumerate(indices_testing) : mse_combined[num] = mse_score_test[i]

        #train_test_tag = np.zeros_like(evnt_numbers) 
        train_test_tag =np.zeros((len(evnt_numbers),))
        train_test_tag[indices_testing] = 1 


        end1 = time.time()
        print(f"Indexing took : {end1-start1}s")

        input_file  = TFile.Open(self.bgd_filepath, "READ") 
        end_f = time.time()
        print(f"Opening file took : {end_f-end1}s")
        output_file = TFile(output_name, "RECREATE")

        for key in input_file.GetListOfKeys():
            name = key.GetName()
            obj  = key.ReadObj()

            print(f"name : {name}")
            print(f"obj : {obj}")
            cycle = key.GetCycle()

            #Change cycle number if file changes 
            if name == "miniT" and obj.InheritsFrom("TTree") and cycle == 25:
                print(f"Modifying bkg tree: {name}")
                tree = obj
                # Clone tree structure only
                new_tree = tree.CloneTree(0)
                
                # Define new branches 
                train_val = array("f", [0])
                mse_val   = array("f", [0]) 
                train_tag_branch = new_tree.Branch("isTrain", train_val, "isTrain/F")
                mse_tag_branch   = new_tree.Branch("mse", mse_val, "mse/F")
                print(f"Tree entries {tree.GetEntries()}")

                # Loop over entries and fill new branch
                for i in range(tree.GetEntries()):
                    tree.GetEntry(i)
                    # Assign train/test tag
                    train_val[0] = train_test_tag[i]
                    # Assign mse score
                    mse_val[0] = mse_combined[i]
                    # Fill tree
                    new_tree.Fill()
                new_tree.Write("miniT", TObject.kOverwrite)
            elif name != "miniT":
                # Write all other objects (TH1D, TH1F, TH1I, etc.) - don't write multiple cycles on miniT
                obj.Write()

        # Close files
        output_file.Close()
        input_file.Close()

        end2 = time.time()
        print(f"File creation took : {end2-end1}s")
        return print(f"Cloned {self.bgd_filepath} to {output_name} and added the branches : isTrain, mse")

    def add_Branch_Sig(self, mse_score_sigs, output_name):
        """
        Create a new root file from the signal  file that contains a tag for: 
        train_test_tag =  1 (all signals used as not used in training) 
        mse_scores = mse score 
        """
        # Define train/test tag - all 1 
        mse_test_score = mse_score_sigs[0]
        train_test_tag = np.ones((len(mse_test_score),))

        #Open original file + make new output file
        input_file  = TFile.Open(self.sig_filepath, "READ") 
        output_file = TFile(output_name, "RECREATE")

        #loop over objects in input file 
        for key in input_file.GetListOfKeys():
            name = key.GetName()
            obj  = key.ReadObj()

            if name == "miniT" and obj.InheritsFrom("TTree"):
                print(f"Modifying signal tree: {name}")
                tree = obj
                # Clone tree structure only
                new_tree = tree.CloneTree(0)

                # Define new branches 
                train_val = array('f', [0])
                mse_val   = array('f', [0])
                train_tag_branch = new_tree.Branch("isTrain", train_val, "isTrain/F")
                mse_tag_branch   = new_tree.Branch("mse", mse_val, "mse/F")
                
                print(f"Tree entries {tree.GetEntries()}")

                # Loop over entries and fill new branch
                for i in range(tree.GetEntries()):
                    tree.GetEntry(i)
                    # Assign train/test tag
                    train_val[0] = train_test_tag[i]
                    # Assign mse score
                    mse_val[0] = mse_test_score[i]
                    #Fill tree
                    new_tree.Fill()
                new_tree.Write()
            else:
                # Write all other objects (TH1D, TH1F, TH1I, etc.)
                obj.Write()

        # Close files
        output_file.Close()
        input_file.Close()
        return print(f"Cloned {self.sig_filepath} to {output_name} and added the branches : isTrain, mse")

def main():
    tree_name = "miniT"
    sigFile   = "frvz_vbf_500757.root"
    bgdFile   = "wjets_strong_sh227.root"
    all_signals = ["frvz_vbf_500757.root"]
    enc_dim = 1 
    epochs_ = 5
    batch_size_ = 2000

    model_AE = SimpleAE(all_signals, sigFile, bgdFile, tree_name)
    #Training + data prep 
    history, BasicAE, recon_test_data, mse_test_data, training_data, testing_data, evnt_nums_full  = model_AE.train(enc_dim, epochs_, batch_size_)
    #Plot loss 
    model_AE.plot_loss(history.history['loss'], history.history['val_loss'], 'log', name = None, save=True, ylim = False)
    #Get Signal Scores 
    mse_sig_scores = model_AE.mse_signals(BasicAE)

    #Plot Signal vs Background MSE 
    model_AE.plot_mse(inp_scores=[mse_test_data]+mse_sig_scores, bins_size=0.1, scale='log', labels=['wjets', 'frvz_vbf_500757'], colours=['r', 'b', 'g'], name=None, xlim=None, save=True)
    #Add branch to root file with train/test tag - BKG
    Evnt_num_training = training_data[:, 0]
    Evnt_num_testing  = testing_data[:, 0]
    model_AE.add_Branch_Bkg(evnt_nums_full, Evnt_num_training, Evnt_num_testing, mse_test_data, output_name=f"Output_{bgdFile}")
    #Add branch to root file with train/test tag - SIG
    model_AE.add_Branch_Sig(mse_sig_scores, output_name=f"Output_{sigFile}")

    return 0 

if __name__=="__main__":
    main()
