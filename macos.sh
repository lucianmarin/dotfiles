# quarantine - mpv example
xattr -d com.apple.quarantine /Applications/mpv.app

# disable disk image verify
defaults write com.apple.frameworks.diskimages skip-verify -bool YES

# enable antialising
defaults write -g CGFontRenderingFontSmoothingDisabled -bool NO

# dmg info
hdiutil imageinfo /PATH/To/DMG | grep 'Format:'

# convert dmg
hdiutil convert /PATH/TO/IMAGE.dmg -format UDBZ -o /PATH/TO/NEW/IMAGE.dmg

# 1, 2, 3 level font smooting
defaults -currentHost write -globalDomain AppleFontSmoothing -int 3

# remove custom font setting
defaults -currentHost delete -globalDomain AppleFontSmoothing

# disable gatekeeper
sudo spctl --master-disable

# codesign apps for Mojave
codesign --sign - --force --deep /Applications/Name.app

# sort Launchpad
defaults write com.apple.dock ResetLaunchPad -bool true; killall Dock

# set font smoothing
defaults write NSGlobalDomain AppleFontSmoothing -int 2

# set dock icon size
defaults write com.apple.dock tilesize -int 28; killall Dock

# make hidden apps transparent in Dock
defaults write com.apple.Dock showhidden -bool YES; killall Dock

# disable chrome swipe
defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool FALSE

# disable screenshots shadows
defaults write com.apple.screencapture disable-shadow -bool true; killall SystemUIServer

# disable desktop icons
defaults write com.apple.finder CreateDesktop true; killall Finder

# disable dashboard
defaults write com.apple.dashboard mcx-disabled -boolean YES; killall Dock

# quicktime autoplay
defaults write com.apple.QuickTimePlayerX MGPlayMovieOnOpen 1

# show hidden files
defaults write com.apple.finder AppleShowAllFiles NO; killall Finder

# install Command Line Tools without Xcode
xcode-select --install

# make usb media
sudo /Applications/Install\ macOS\ High\ Sierra.app/Contents/Resources/createinstallmedia --volume /Volumes/Untitled/ --applicationpath /Applications/Install\ macOS\ High\ Sierra.app/

# Mojave, macOS 10.14+
sudo /Applications/Install\ macOS\ Mojave.app/Contents/Resources/createinstallmedia --volume /Volumes/Untitled

# indexing on disk images
sudo mdutil -i on /Volumes/Name
sudo mdutil -i off /Volumes/Name

# disable spotlight
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist

# enable spotlight
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist

# disable versioning
# set Ask to keep changes… in System Preferences › General
defaults write -g ApplePersistence -bool no
sudo rm -rf /.DocumentRevisions-V100

# enable codecs
sudo defaults write bluetoothaudiod "Enable AptX codec" -bool true
sudo defaults write bluetoothaudiod "Enable AAC codec" -bool true
sudo defaults write bluetoothaudiod "Apple Initial Bitpool" 40
sudo defaults write bluetoothaudiod "Apple Bitpool Min" 24
sudo defaults write bluetoothaudiod "Apple Bitpool Max" 48

# sudo touch id
/etc/pam.d/sudo
auth sufficient pam_tid.so
