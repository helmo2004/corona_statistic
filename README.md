# corona_statistics
You need python 3.6 with the following modules:
```
pip3 install matplotlib numpy mpld3 jinja2
```

Clone repository and change your directory to this path: 
```
git clone https://github.com/helmo2004/corona_statistics.git
cd corona_statistics
```

You can simply run:
```
python3 .
```

By default statistics for a list of predefined countries are generated,
but you can also provide them by commandline to overwrite default list
```
python3 . "Germany" "Austria"
```

Script will generate a "index.html" that can be opened with a browser of your choice:
```
firefox index.html
```
