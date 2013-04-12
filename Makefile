EGOFEEDER=target/EgoFeeder.exe

all: $(EGOFEEDER)

$(EGOFEEDER): src/EgoFeeder.py
	cxfreeze src/EgoFeeder.py --target-dir target --base-name Win32GUI --include-modules PIL,cv2,win32gui

deploy:
	cp src/config.ini target/
	cp src/AutoHotkey.dll target/
	cp -R src/img target/img

clean:
	rm -rf target/*
