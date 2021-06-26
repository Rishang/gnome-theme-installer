URL="https://www.gnome-look.org/s/Gnome/p/1253385/"
export TEST_THEME_INSTALLER=true

run:
	python3 gnomelooks.py -i ${URL}

sudo_run:
	sudo python3 gnomelooks.py -i ${URL}
