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

function _test_requirement_packages
{
    echo -e "Checking if needed packages exist.\n"
    local needed=("curl" "git" "python3" "pip3" "curl")
    
    for p in ${needed[@]};do
        if ! [[ `command -v "$p"` ]];then
            echo "Error: package $p not found."
            echo -e "\ninstall needed packages. and try again."
            echo -e "\nRun: sudo $package_installer install -y curl git python3 python3-pip curl gnome-tweaks"
            echo 
            return 1
        fi
    done
}


# Install user-theme extension of not present
function _user_theme_ext()
{
    user_theme=$(echo $ext_path/$UUID)
    
    if ! [ -e $user_theme ];then
        echo "getting user-theme extension for gnome tweaks."
        user_theme_dir="$ext_path/$UUID"
        theme_ext_url="https://extensions.gnome.org/extension-data/user-themegnome-shell-extensions.gcampax.github.com.v42.shell-extension.zip"
        theme_ext_zip="user-themegnome-shell-extensions.gcampax.github.com.v42.shell-extension.zip"
        curl -sS "$theme_ext_url"  -o "/tmp/$theme_ext_zip"
        
        mkdir -p $user_theme_dir
        unzip /tmp/$theme_ext_zip -d $user_theme_dir
    
    else
        echo "Extension: user-themes exist."
    fi
}

# install gnomelook script
function _gnomelooks_setup()
{   
    if ! [ -e "$HOME/.local/bin" ];then
        mkdir -p "$HOME/.local/bin"
        echo 'export PATH=$HOME/.local/bin:$PATH' >> $HOME/.bashrc
    fi
    

    pip3 install $(curl -fsSl "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/requirements.txt")
    
    echo -e "\n Cloaning gnome-theme-installer at ~/.gnomelooks"
    git clone --depth 1 "https://github.com/Rishang/gnome-theme-installer.git" $gnomelooks_path
    
    chmod +x "$gnomelooks_path/gnomelooks.py"

    echo -e "Done\n"
}

# check this first, and only then continue
if ! _test_requirement_packages;then exit 1;fi

# check if folder for user-theme ext exist
if [ -e $ext_path ];then
    _user_theme_ext
else
    mkdir -p $ext_path
    _user_theme_ext
fi

# check if gnomelooks exists
if ! [ -e $gnomelooks_path ];then
    
    _gnomelooks_setup
    # soft link
    echo -e "\e[32m \nDone\nNOTE:  Link gnomelooks to /usr/local/bin  by copying the  command  given  below.\n"
    
    echo -e "COPY: \e[36msudo ln -s $gnomelooks_path/gnomelooks.py /usr/local/bin/gnomelooks && exec bash\e[39m"

    echo -e "\nAfter executing above line, type \e[32mgnomelooks\e[39m"
    
else
    echo "gnomelooks Exists"
    cd $gnomelooks_path
    git pull origin master
    cd -
fi
