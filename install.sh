# check if gnome  or not
if ! [[ $(command -v gnome-shell) ]];then echo "Error: gnome shell not found"; exit 1 ;fi

gnomelooks_path="$HOME/.local/bin/gnomelooks"
ext_path="$HOME/.local/share/gnome-shell/extensions"
UUID="user-theme@gnome-shell-extensions.gcampax.github.com"

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
    if ! [ -e "$HOME/.local/bin" ];then mkdir -p "$HOME/.local/bin";fi
    pip3 install $(curl -fsSl "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/requirements.txt")
    
    curl -fsS "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/gnomelooks.py" -o $gnomelooks_path
    chmod +x $gnomelooks_path
    echo  "Restart terminal and type gnomelooks"
}

# check if folder for user-theme ext esists
if [ -e $ext_path ];then
    user_theme_ext
else
    mkdir -p ext_path
    user_theme_ext
fi

# check if gnomelooks exists
if ! [ -e $gnomelooks_path ];then
    gnomelooks_setup
else
    echo "gnomelooks Exists"
fi
