#include "AtlasStyle.C"
#include "AtlasUtils.C"
void rootlogon()
{
  // Load ATLAS style
  gROOT->LoadMacro("AtlasStyle.C");
	gROOT->LoadMacro("AtlasUtils.C");
  SetAtlasStyle();
}
