# the data
[remap.json](remap.json) contains a reverse mapping of Village names to their corresponding District, Taluk and Hobli names

# why?
Some documents/information on the [kaveri website](https://kaveri.karnataka.gov.in/) ask you to select your Village from a drop down. This drop down is preceded by a District, a Taluk and a Hobli drop down, each filled based on the previous selections. Finding your Village requires a lot of trial and error to get the right options selected.

# the process
An initial list of Districts is scraped from the website's static data. Using post-login headers, loops are run on each selection and data is collected using the internal APIs (respecting the rate limits). Each District gives a list of Taluks, each Taluk a list of Hoblis and each Hobli a list of Villages. This data is saved, deduplicated and a reverse mapping is created. 
