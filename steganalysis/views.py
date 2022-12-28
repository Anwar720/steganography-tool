from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django import template
from stegano import lsb
from PIL import Image
from operator import itemgetter
import numpy as np
import sys
import os
from stegano import exifHeader

module_path = os.path.abspath(os.getcwd())
if module_path not in sys.path:
    sys.path.append(module_path)
register = template.Library()


def home(request):
    return render(request, 'home.html')

def hideDataInJPG(image_path,secret):
    secret = exifHeader.hide((image_path),
                        "./steganalysis/static/img/image.jpg",
                        secret_message=secret)

def detectDataInJPG(image_path,name):
    result = exifHeader.reveal(image_path)
    print(result)
    return {
        'output': 'detect',
        "input": name,
        "result": result
    }

def hideData(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        img = request.FILES['img']
        fs = FileSystemStorage()
        fs.save(img.name, img)
        
        # check if image is jpg then hide using jpg function
        if '.jpg' in request.FILES['img'].name:
            image_path = './steganalysis/static/img/' + img.name
            hideDataInJPG(image_path,message)
            return render(request, 'home.html', {
            'output': 'hide',
            "input": img.name,
            "result": "img/image.jpg"
            })
            
        # hide message in image and save
        secret = lsb.hide(img, message)
        secret.save("./steganalysis/static/img/tempStegImg.png")
        print('message hidden')
        # delete original image
        os.remove('./steganalysis/static/img/' + img.name)

        return render(request, 'home.html', {
            'output': 'hide',
            "input": img.name,
            "result": "/img/tempStegImg.png"
        })


def image_analysis(request):
    if request.method == 'POST':
        img = request.FILES.get('image')
        try:
            os.remove('./steganalysis/static/img/' + img.name)
        except:
            print('check - Not in system...Download File...')
        print('image is ',img)
        fs = FileSystemStorage()
        fs.save(img.name, img)
        path = "./steganalysis/static/img/" + img.name
    
        # check for jpg
        if '.jpg' in img.name:
            return render(request, 'home.html',detectDataInJPG(path,img.name))
        
        #png and other image types 
        result = lsb.reveal(path)
        
        url_data = ''
        try:
            if not len(result):
                url_data = test_url(path)
        except:
            print('Url function return empty')

    return render(request, 'home.html', {
        'output': 'detect',
        "input": img.name,
        "result": url_data +"\n"+ result
    })



def test_url(image_source):
    # opening the text file containing popular domains and reading the data
    domain_file = open("./steganalysis/static/tlds-alpha-by-domain.txt", "r")
    domain = domain_file.read()
    domain = domain.split('\n')
    domain_file.close()
    # opening the image and reading data into numpy array 
    # image = Image.open("./steganalysis/static/img/tempStegImg.png")
    image = Image.open(image_source)
    np_img = np.array(image)
    image.close()

    # creating a bitmap array by reading each bit from the image
    bitmap = []
    for i in np_img:
        for j in i:
            for k in j:
                bitmap.append(np.binary_repr(k))
    bitmap = np.array(bitmap)
    # creating an array with the least significant bits
    lsb_arr = []
    for i in range(len(bitmap)-1):
        lsb_arr.append(bitmap[i][-1])

    # grouping the bits into bytes
    c = 1
    k = 0
    lsb_byte_arr = []
    for j in range(len(lsb_arr)-1):
        if(c % 8 == 0):
            lsb_byte_arr.append(lsb_arr[c-8:c])
            k += 1
        c += 1

    lsb_ascii_arr = []
    lsb_bin_arr = []
    lsb_int_arr = []
    # joining the bits in the bytes together
    for i in lsb_byte_arr:
        lsb_bin_arr.append(''.join(map(str,i)))

    # converting the binary into int
    for i in lsb_bin_arr:
        lsb_int_arr.append(int(i, base=2))

    # converting the int into the ascii characters 
    # found in an url: a-z A-Z 0-9 - . _ ~
    for i in lsb_int_arr:
        if (i >= 48 and i <=57) or (i >= 65 and i <= 90) or (i >= 97 and
                        i <= 122) or (i >= 45 and i <= 46) or i == 95 or i == 126:
            lsb_ascii_arr.append(chr(i))

    # converting the ascii list to a string to use some functions
    # exclusive to str
    lsb_ascii_str = ''.join(lsb_ascii_arr)
    #uncomment these lines for testing
    # strings="sffsbdgfsdcf2342c224c4https://www.google.aaasadas"
    # l = list(strings)
    # lsb_ascii_arr = l + lsb_ascii_arr
    # lsb_ascii_str = strings + lsb_ascii_str

    url_found = ''
    httpFound = False
    httpsFound = False
    domainFound = False
    http_index = 0
    https_index = 0
    max_domain_len = len(max(domain,key=len))
    distance_to_http = []
    distance_to_https = []
    lower_domains = []
    i = 0
    j = 0
    # for loop that iterates through the ascii values checking if http or https is found
    # if so that position is marked and a bool is set to true. if a . is found while a http method 
    # has been found and domain hasn't been found another for loop iterates through all domain values
    # comparing them against lsb_ascii_str and appending the indices to a list along with the distance 
    # between . and http(s)
    for i in range(len(lsb_ascii_arr)-1):
        if i >=4 and lsb_ascii_str[i-4:i] == 'http' and (httpFound == False and httpsFound == False):
            httpFound = True
            http_index = i
            url_found = url_found.join(lsb_ascii_arr[i-4:i])
        if i >=5 and lsb_ascii_str[i-5:i] == 'https' and (httpFound == False and httpsFound == False):
            httpsFound = True
            https_index = i
            url_found = url_found.join(lsb_ascii_arr[i-5:i])
        if lsb_ascii_arr[i] == '.' and domainFound == False and (httpFound == True or httpsFound == True):
            period_found = i
            for j in range(len(domain)-1):
                if httpFound == True and domain[j] in lsb_ascii_str:
                    distance_to_http.append([period_found - http_index, period_found])
                    break
                elif httpsFound == True and domain[j] in lsb_ascii_str:
                    distance_to_https.append([period_found - https_index, period_found])
                    break
    # distance_to_http lets us sort out periods followed by domains not close to the url
    distance_to_http = sorted(distance_to_http,key=itemgetter(0))

    # another for loop iterating through domain and checking if the domain is in the
    # slice of the string from period_found to period_found + length of longest domain
    # if a domain is found it is appended into another list from which the domain is 
    # chosen. the url is made up of http(s) + everything in between + domain found
    for u in domain:
        if '.'+u.lower() in lsb_ascii_str[distance_to_http[0][1]:distance_to_http[0][1]+max_domain_len]:
            lower_domains.append('.'+u.lower())
    lower_domains = sorted(lower_domains,key=len)
    lower_domain = lower_domains[1]
    domainFound = True
    k = lsb_ascii_str.find(lower_domain)
    if httpFound == True:
        url_found = url_found + (lsb_ascii_str[http_index:k]) + lower_domain    
    elif httpsFound == True:
        url_found = url_found + (lsb_ascii_str[https_index:k]) + lower_domain

    return url_found

