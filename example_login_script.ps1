#this assumes your package installer in PDQ creates a desktop shortcut for the logged in user

# This is the group to check if user is member of
$group = "your AD group that needs something installed"

# API endpoints for install/uninstall
$install_package = {Invoke-WebRequest "http://yourserver:8080/deploy/package_installer_name_goes_here/$env:computername"}
$remove_package = {Invoke-WebRequest "http://yourserver:8080/deploy/package_uninstaller_name_goes_here/$env:computername"}

#paths
$InstallationDIR = 'C:\yourappinstallationdir'
$DesktopShortcut = [Environment]::GetFolderPath('Desktop') + "\shortcut.lnk"
$DesktopShortcut_master = "\\yourserver\Software\yourapp\shortcut.lnk"


# Get the current user's username and domain
$username = [Environment]::UserName
$domain = [Environment]::UserDomainName

# Load the .NET assembly
Add-Type -AssemblyName System.DirectoryServices.AccountManagement

# Create a principal context for the domain
$pc = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Domain, $domain)

# Get the user and group
$user = [System.DirectoryServices.AccountManagement.UserPrincipal]::FindByIdentity($pc, $username)
$group = [System.DirectoryServices.AccountManagement.GroupPrincipal]::FindByIdentity($pc, $group)

# If the user is a member of the group, call the API to install
if ($user.IsMemberOf($group)) {
    echo "You need THE APP"
    
    	#check for installation
    if (Test-Path -Path $InstallationDIR) {
        echo "THE APP is already installed"
        
        #check for desktop shortcut
		if (Test-Path -Path $DesktopShortcut) {
			echo "THE APP Shortcut already exists"
		} else {
			echo "THE APP Desktop shortcut does not exist but it should. creating"
			& Copy-Item -Path $DesktopShortcut_master -Destination $DesktopShortcut
		}

    } else {
        echo "THE APP Client is not installed. Asking PDQ to install"
		& $install_package
    }
    
}

# If user is NOT a member of the group, check for THE APP client/shortcut and remove
if (-not $user.IsMemberOf($group)) {
    echo "You do not need THE APP"

	#check for installation
    if (Test-Path -Path $InstallationDIR) {
        echo "THE APP is installed but it should not be. Asking PDQ to uninstall"
		& $remove_package
    } else {
        echo "THE APP is not installed"
    }
    
    #check for desktop shortcut
    if (Test-Path -Path $DesktopShortcut) {
        echo "THE APP Shortcut exists but it should not. Removing desktop shortcut"
        Remove-Item -Path $DesktopShortcut
    } else {
        echo "THE APP Desktop shortcut does not exist"
    }   
}
