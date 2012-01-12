import gettext

gettext.bindtextdomain('trs', 'lang')
gettext.textdomain('trs')

_ = gettext.gettext
