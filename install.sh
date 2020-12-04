# check if gnome  or not
if ! [[ $(command -v gnome-shell) ]];then echo "Error: gnome shell not found"; exit 1 ;fi

gnomelooks_path="$HOME/.gnomelooks"

ext_path="$HOME/.local/share/gnome-shell/extensions"
UUID="user-theme@gnome-shell-extensions.gcampax.github.com"

if [[ `command -v apt` ]];then
    package_installer="apt"
elif [[ `command -v yum` ]];then
    package_installer="yum"
fi

function test_requirement_packages
{
    echo -e "Checking if needed packages exist.\n"
    local needed=("curl" "git" "python3" "pip3" "curl" "gnome-tweaks")
    
    for p in ${needed[@]};do
        if ! [[ `command -v "$p"` ]];then
            echo "Error: package $p not found."
            echo -e "\ninstall needed packages. and try again."
            echo -e "\nRun: sudo $package_installer install curl git python3 python3-pip curl gnome-tweaks"
            echo 
            return 1
        fi
    done
}


# Install user-theme extension of not present
function user_theme_ext()
{
    user_theme=$(echo $ext_path/$UUID)
    
    if ! [ -e $user_theme ];then
        echo "getting user-theme extension for gnome tweaks."
        user_theme_dir="$ext_path/$UUID"
        theme_ext_url="https://extensions.gnome.org/extension-data/user-themegnome-shell-extensions.gcampax.github.com.v41.shell-extension.zip"
        theme_ext_zip="user-themegnome-shell-extensions.gcampax.github.com.v41.shell-extension.zip"
        curl -sS "$theme_ext_url"  -o "/tmp/$theme_ext_zip"
        
        mkdir -p $user_theme_dir
        unzip /tmp/$theme_ext_zip -d $user_theme_dir
    
    else
        echo "Extension: user-themes exise."
    fi
}

# install gnomelook script
function gnomelooks_setup()
{   
    if ! [ -e "$HOME/.local/bin" ];then
        mkdir -p "$HOME/.local/bin"
        echo 'export PATH=$HOME/.local/bin:$PATH' >> $HOME/.bashrc
    fi
    

    pip3 install $(curl -fsSl "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/requirements.txt")
    
    echo -e "\n Cloaning gnome-theme-installer at ~/.gnomelooks"
    git clone --depth 1 "https://github.com/Rishang/gnome-theme-installer.git" $gnomelooks_path
    
    chmod +x "$gnomelooks_path/gnomelooks.py"

    # soft link
    echo -e "\n linking gnomelooks.py to ~/.local/bin/gnomelooks"
    ln -s "$gnomelooks_path/gnomelooks.py" "$HOME/.local/bin/gnomelooks"
    
    echo -e "Done\n"
    echo  "Restart terminal and type gnomelooks"
}

# check this first, and only then continue
if ! test_requirement_packages;then exit 1;fi

# check if folder for user-theme ext exist
if [ -e $ext_path ];then
    user_theme_ext
else
    mkdir -p $ext_path
    user_theme_ext
fi

# check if gnomelooks exists
if ! [ -e $gnomelooks_path ];then
    gnomelooks_setup
else
    echo "gnomelooks Exists"
fi
