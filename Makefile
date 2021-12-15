.ONESHELL: # Applies to every targets in the file! https://www.gnu.org/software/make/manual/html_node/One-Shell.html

URL="https://www.gnome-look.org/s/Gnome/p/1253385/"
export TEST_THEME_INSTALLER=true

run:
	cd looks-install
	python3 cli.py get ${URL}

sudo_run:
	cd looks-install
	sudo python3 cli.py get ${URL}
