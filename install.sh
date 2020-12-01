# check if gnome  or not
#if ! [[ $(command -v gnome-shell) ]];then echo "Error: gnome shell not found"; exit 1 ;fi

gnomelooks_path="$HOME/.local/bin/gnomelooks"
ext_path="$HOME/.local/share/gnome-shell/extensions"
UUID="user-theme@gnome-shell-extensions.gcampax.github.com"

# Install user theme extension of not present
function user_theme_ext()
{
    user_theme=$(echo $ext_path/$UUID)
    
    if ! [ -e $user_theme ];then
        user_theme_dir="$ext_path/$UUID"
        
        wget https://extensions.gnome.org/extension-data/user-themegnome-shell-extensions.gcampax.github.com.v41.shell-extension.zip  -P /tmp
        
        mkdir -p $user_theme_dir
        unzip /tmp/user-themegnome-shell-extensions.gcampax.github.com.v41.shell-extension.zip -d $user_theme_dir
    
    else
        echo "Extension: user-themes exise."
    fi
}

function gnomelooks_setup()
{   
    if ! [ -e "$HOME/.local/bin" ];then mkdir -p "$HOME/.local/bin";fi
    pip3 install $(curl -fsSl "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/requirements.txt")
    
    curl -fsS "https://raw.githubusercontent.com/Rishang/gnome-theme-installer/master/gnomelooks.py" -o $gnomelooks_path
    chmod +x $gnomelooks_path
    echo  "Restart terminal and type gnomelooks"
}

if [ -e $ext_path ];then
    user_theme_ext
else
    mkdir -p ext_path
    user_theme_ext
fi

if ! [ -e $gnomelooks_path ];then
    gnomelooks_setup
fi
