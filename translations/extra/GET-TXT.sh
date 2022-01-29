#!/bin/bash

echodo() {
  echo "${@@Q}"
  ${@}
}

# prepare transifex 
if [ ! -s  .tx/config ]; then
   mkdir -p .tx
   cat <<EOF > .tx/config
[main]
host = https://www.transifex.com

[antix-development.mx-all-desktop-entries]
file_filter = <lang>.txt
minimum_perc = 0
source_file = EN.TXT
source_lang = en
type = txt
EOF
fi    


# remove existing
rm *.TXT *.txt *.po *.po?  *.tmp *.PO* 2>/dev/null

# get all mx-all-desktop-entries translations
if command -v tx >/dev/null; then
   echodo tx pull -s -r antix-development.mx-all-desktop-entries --all
fi


sed -i -e '1,4d; 7d; 9,$d; s/^[^=]*=//; s/.*/msgid "&"/'  EN.TXT
sed -i -e '1,4d; 7d; 9,$d; s/^[^=]*=//; s/.*/msgstr "&"/'  *.txt
sed -i -r 's/msgstr "(MX Updater|An applet to show updates|Re-enable MX Updater icon even if no updates available)"/msgstr ""/'  *.txt

sed -e '/msgid/amsgstr ""\n' EN.TXT > EN.POT

./POL-PO.py
[ -s EN.POL ] && cat EN.POL >> EN.POT

for T in *.txt; do 
  LL="${T%.txt}"
  [ -f ../po/$LL.po ] || continue

  PO=$LL.po
  POD=$LL.pod
  POH=$LL.poh
  POL=$LL.pol
  POM=$LL.pom
  POT=$LL.pot

  msgmerge --no-fuzzy-matching --no-wrap  ../po/$LL.po ../en.pot -o $POT

  msggrep -o $POH --force-po -K -e '^$' ../po/$LL.po 
   
  paste -d'\n'  EN.TXT $T > $POM
  sed -i 's/^msgid/\n&/' $POM
  cat  $POH  $POM > $POD.tmp
  
  [ -s $POL ] && cat $POL >> $POD.tmp
   
  msggrep  --no-wrap -T -e '..'  $POD.tmp -o $POD 

  if [ -s $POD ]; then  
	msg_pot=$(msggrep --no-wrap -K -e '^MX Updater$' $POT | grep -oP 'msgstr "\K[^"]+')
	msg_pod=$(msggrep --no-wrap -K -e '^MX Updater$' $POD | grep -oP 'msgstr "\K[^"]+')
	if [[ $msg_pot ==  $msg_pod ]]; then
		mv $POD $POD.tmp
		msggrep -v --no-wrap -K -e '^MX Updater$' $POD.tmp  -o $POD 
	fi
  fi
  
  if [ -s $POD ]; then  
	msgmerge -N  --no-wrap  $POD $POT -o $PO
  else
    :     
  fi
  
done

for PO in *.po; do
   cp $PO ../po
done
rm *.po

for POD in *.pod; do
   mv $POD ${POD%.pod}.po
done
   
rm *.txt *.po? *.tmp 2>/dev/null
rm *.TXT *.PO* 2>/dev/null
