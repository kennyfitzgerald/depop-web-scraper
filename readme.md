# Depop web scraping tool

This program uses web scraping package BeautifulSoup to
pull data from the Depop website. When an item is found that matches any of the user specified criteria, 
the a notification sound is played and the item url is opened in the browser. 

The inspiration came from my own experiences with the app. If there was a specific item I wanted then 
I would constantly find myself searching the same things each time in hope that one with a suitable price
and condition would pop up. This was time consuming, so I thought that this project would be not only some good practice 
for my Python skills, but also a really useful tool to have.

### Requirements

1. Python (3.8.5)
2. BeautifulSoup
3. Threading
4. Pandas
5. WinSound
6. Socket

### Getting started 

If you take a look in the search_config.ini file then you can see multiple sections in the format 'search_xxx'
where xxx is a string of numbers e.g. 001. As many searches can be added to this as you please, so long 
as they stick to this format. The parameters than can be specified for each search are as follows:

- query: The search term.
- sizes: A list of sizes you'd be happy with for this particular item. These must be comma separated.
- min_price: Obvious
- max_price: Ditto
- interval: How many minutes to wait between each search before trying again.
- filter_desc: A comma separated list of terms. If the description contains any of these, then the item will be ignored.

Further to these parameters which are adjustable for each item, there is also a couple of universal lists. These are 
under the 'blacklist' section. The first is for users. If there is a user that you don't want to keep seeing results from
then simply add them to this comma separated list. The second is for terms. Whilst you can filter terms from the description,
there are some cases in which you want to filter from every search. These can be added here and it will apply to all searches.
This list is useful for terms such as 'womens' if you're male, or 'well worn' if you prefer your clothes a bit fresher.

Once you've set up the configuration file then it should be as easy as running the main script (Or the batch script, which
I've included for my own convenience).
