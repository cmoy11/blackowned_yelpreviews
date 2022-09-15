from bs4 import BeautifulSoup
from pyparsing import alphas
import requests
import re
import csv
import os

API_KEY = "KrlCoAsmMTGJftfD6uV-s7kSN0o-SG2anMcTrwP6G4szLC3AsKX-hbiVLqiBfMj371sNemBCzrN8zCHae5SgIp1jqoiExhvExitIroX4_mBzQgWVtxcXFdFQIkkNYnYx"

# Black-owned restaurants scrapper 
def get_black_owned():
    url = "https://seenthemagazine.com/25-black-owned-restaurants-in-metro-detroit/"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    restaurants = soup.find_all('h3')
    stripped_restaurants = []
    for r in restaurants[:27]:
        stripped_restaurants.append(r.text.strip())
    print('done scraping restaurants')
    return stripped_restaurants
    
    # stripped_restaurants = ['Peteet’s Famous Cheesecakes', 'House of Pure Vin', 'Sweet Potato Sensations', 'Detroit Sip', 'Ima Noodles', 'Good Cakes and Bakes', 'Kuzzo’s Chicken and Waffles', 'Savannah Blue', 'The Jamaican Pot', 'Detroit Soul', 'Yum Village', 'Baker’s Keyboard Lounge', 'City Wings', 'Le Culture Cafe', 'The Block Detroit', 'Dime Store', 'Ellis Island Tropical Tea', 'GO! Smoothies', 'Detroit Vegan Soul', 'Detroit Seafood Market', 'Flood’s Bar and Grille', 'Central Kitchen and Bar', 'Beans & Cornbread', 'Brix Wine & Charcuterie Boutique', 'Dilla’s Delights', 'They Say Restaurant', 'The Breakfast Loft']

# hyphenate the restaurants to match the yelp url format
def hyphenate(stripped_restaurants):
    hyphen_restaurants = []
    for restaurant in stripped_restaurants:
        str = ""
        for char in restaurant:
            if char.isalpha():
                str += char.lower()
            elif char == " ":
                str += "-"
            elif char == "&":
                str += "and"
        hyphen_restaurants.append(str)
    print('done hyphenating')
    return hyphen_restaurants

    # hyphen_restaurants = ['peteets-famous-cheesecakes', 'house-of-pure-vin', 'sweet-potato-sensations', 'detroit-sip', 'ima-noodles', 'good-cakes-and-bakes', 'kuzzos-chicken-and-waffles', 'savannah-blue', 'the-jamaican-pot', 'detroit-soul', 'yum-village', 'bakers-keyboard-lounge', 'city-wings', 'le-culture-cafe', 'the-block-detroit', 'dime-store', 'ellis-island-tropical-tea', 'go-smoothies', 'detroit-vegan-soul', 'detroit-seafood-market', 'floods-bar-and-grille', 'central-kitchen-and-bar', 'beans-and-cornbread', 'brix-wine-and-charcuterie-boutique', 'dillas-delights', 'they-say-restaurant', 'the-breakfast-loft']

def get_reviews(hyphen_restaurants, city):
    non_valid = []
    reviews = {}
    for restaurant in hyphen_restaurants:
        print(restaurant)
        # create the restaurant's url using the hyphenated names and provided city
        url = f"https://www.yelp.com/biz/{restaurant}"
        print(url)
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')

        review_information = {}
        reviews_list = []
        regex = r"(\d+)\sreviews"
        regex2 = r"\d{1,2}\/\d{1,2}\/\d{4}"

        # extract comments, ratings, and review count from the restaurant's main Yelp page
        first_ten = soup.find_all('p', class_="comment__09f24__gu0rG")

        # skips restaurant if not in city/url does not exist
        if first_ten == []:
            print(f"{restaurant} is not in {city}")
            non_valid.append(restaurant)
            continue 

        first_ten_stars = soup.find_all('div', class_="i-stars__09f24__M1AR7")
        raw_first_ten_dates = soup.find_all('span', class_="css-chan6m")
        num_reviews_extract = soup.find_all('span', class_='css-1fdy0l5')

        # extract review dates
        first_ten_dates = []
        for date in raw_first_ten_dates:
            reg_input = re.findall(regex2, date.text)
            if reg_input != []:
                first_ten_dates.append(reg_input)

        # get the number of reviews using regex expression
        for review in num_reviews_extract:
            reg_input = re.findall(regex, review.text)
            if reg_input != []:
                num_reviews = int(reg_input[0])
                review_information['number of reviews'] = num_reviews
        print(f"{restaurant} has {num_reviews} reviews") 

        # builds a dictionary for the first 10 reviews
        for i in range(len(first_ten)):
            rating = first_ten_stars[i+1]['aria-label']
            review = first_ten[i].text.strip()
            review_d = {}
            review_d['date'] = first_ten_dates[i][0]
            review_d['rating'] = rating
            review_d['review'] = review
            reviews_list.append(review_d)

        # loops through the remaining reviews and adds to review dictionary
        # Note there are some descrepancies between the number of reviews scraped from the Yelp page header and the number 
        # returned from the scraping. I.e. sweet potato sensations has 135 reviews according to yelp, but the code returns 138 reviews.
        # This is due to an owner responding to a review or the double counting of multiple reviews - let's say a user reviews a restaurant in 2014, then they review again in 2021, these reviews would be linked and the original review would be double counted.
        # Tried a couple of different duplicate remvoal strategies, but all of them resulted in lost data
        # If we do analysis with the resulatant csv files, prbably easiest to manually remove duplicates in excel
        counter = 10
        while num_reviews > counter:
            new_url = url + f"?start={str(counter)}"
            print(new_url)
            soup = BeautifulSoup(requests.get(new_url).text, 'html.parser')
            next_ten = soup.find_all('p', class_="comment__09f24__gu0rG")
            next_ten_stars = soup.find_all('div', class_="i-stars__09f24__M1AR7")
            raw_next_ten_dates = soup.find_all('span', class_="css-chan6m")

            next_ten_dates = []
            for date in raw_next_ten_dates:
                reg_input = re.findall(regex2, date.text)
                if reg_input != []:
                    next_ten_dates.append(reg_input)

            for i in range(len(next_ten)):
                rating = next_ten_stars[i+1]['aria-label']
                review = next_ten[i].text.strip()
                review_d = {}
                review_d['date'] = next_ten_dates[i][0]
                review_d['rating'] = rating
                review_d['review'] = review
                reviews_list.append(review_d)

            counter += 10
        review_information['Yelp user reviews'] = reviews_list
        reviews[restaurant] = review_information

        # writes csv files for each restaurant
        filename = f"{city}/not-black-owned/review_csvs/{restaurant}.csv"
        with open(filename, "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["date", "rating", "review"])
            for subd in reviews[restaurant]['Yelp user reviews']:
                date = subd['date']
                rat = subd['rating']
                rev = subd['review']
                csvwriter.writerow([date, rat, rev])
        print(f'done with {restaurant}')

    # prints number of reviews and the number of reviews scraped to see how many duplicates we have
    # writes csv file of reviews for each restaurant
    for key in reviews:
        print(key)
        print(reviews[key]['number of reviews'])
        print(len(reviews[key]['Yelp user reviews']))

    return non_valid

def main():
    print('starting')
    # restaurants = get_black_owned()
    restaurants = ['royal-grill-restaurant-detroit-2', 'royale-with-cheese-detroit', 'rusted-crow-detroit-detroit-2', 'saffron-de-twah-detroit', 'sala-thai-detroit', 'san-morello-detroit', 'savant-detroit-3', 'savvy-sliders-detroit-2', 'scotty-simpsons-fish-and-chips-detroit', 'selden-standard-detroit', 'senor-lopez-mexican-restaurant-detroit', 'seva-detroit-detroit', 'seven-mile-shrimp-palace-detroit', 'sheeba-express-detroit-5', 'sheilas-bakery-detroit', 'shewolf-pastificio-and-bar-detroit', 'shields-restaurant-bar-pizzeria-detroit-3', 'shredderz-food-truck-detroit', 'shrimp-city-detroit-detroit', 'simply-spanish-detroit-2', 'sinai-grace-hospital-cafeteria-detroit', 'sindbads-restaurant-and-marina-detroit', 'sky-bar-and-grill-detroit-2', 'sliders-313-detroit', 'slows-bar-bq-detroit', 'slows-to-go-detroit', 'smith-and-co-detroit', 'socra-tea-detroit-detroit-2', 'something-good-aka-chef-dees-detroit', 'sonnys-hamburgers-detroit', 'southern-fires-bistro-and-lounge-detroit', 'spread-detroit-detroit-3', 'stache-international-detroit', 'standby-detroit', 'starters-bar-and-grill-detroit-2', 'street-cuisine-detroit', 'sullaf-restaurant-detroit', 'sun-china-detroit', 'sun-sun-restaurant-detroit', 'supergeil-detroit', 'sweetwater-express-detroit-2', 'sweetwater-express-detroit-detroit', 'sweetwater-tavern-detroit', 't-mos-bbq-pit-detroit', 'tacos-el-caballo-detroit', 'tacos-el-toro-detroit', 'tai-hing-detroit', 'takoi-detroit', 'tamaleria-nuevo-leon-detroit', 'taquería-chilango-detroit', 'taqueria-lupitas-detroit', 'taqueria-mi-pueblo-detroit', 'taqueria-nuestra-familia-detroit-2', 'taylor-made-phat-burgers-detroit-2', 'telway-hamburgers-detroit', 'the-apparatus-room-detroit', 'the-baltimore-detroit', 'the-clique-restaurant-detroit', 'the-congregation-detroit-detroit', 'the-dakota-inn-rathskeller-detroit', 'the-detroit-pepper-company-detroit', 'the-drunken-rooster-detroit', 'the-elephant-room-detroit', 'the-greek-detroit', 'the-hudson-cafe-detroit', 'the-london-chop-house-detroit-2', 'the-old-shillelagh-detroit', 'the-peterboro-detroit-2', 'the-potato-place-detroit', 'the-rattlesnake-club-detroit', 'the-whitney-detroit', 'tommys-detroit-bar-and-grill-detroit', 'toney-island-detroit-2', 'tony-vs-tavern-detroit', 'topeys-kitchen-detroit', 'torta-express-detroit', 'tortitas-el-rojito-detroit', 'townhouse-detroit', 'traffic-jam-and-snug-detroit-3', 'tres-leches-n-snacks-tacos-detroit', 'triangulo-dorado-detroit', 'trinosophes-detroit', 'u-of-d-coney-island-detroit', 'ufo-factory-detroit-2', 'uncle-rays-potato-chips-detroit', 'uptown-barbecue-detroit', 'urban-ramen-detroit-2', 'veggininis-paradise-cafe-detroit-2', 'vertical-detroit-detroit', 'vicentes-cuban-cuisine-detroit', 'victory-liquor-and-food-store-detroit-2', 'vivios-food-and-spirits-detroit', 'volt-detroit', 'wild-wild-west-wings-detroit', 'wings-chinese-restaurant-detroit', 'woodbridge-pub-detroit', 'woodward-coney-restaurant-detroit', 'woodward-market-detroit', 'wright-and-company-detroit-3', 'xochimilco-restaurant-detroit', 'yellow-light-coffee-and-donuts-detroit', 'zs-villa-detroit', 'zeffs-coney-island-in-eastern-market-detroit', 'zos-good-burger-detroit-2', 'zorbas-coney-island-detroit-4']
    
    # LA Black Owned: ['delvigne-croissant-culver-city', 'derricks-on-atlantic-long-beach', 'devis-donuts-and-sweets-long-beach', 'dirty-south-soulfood-south-gate-2', 'divine-dips-vegan-ice-creme-los-angeles-2', 'doll-babee-cheesecakes-lakewood-2', 'dulans-on-crenshaw-los-angeles', 'dulans-soul-food-kitchen-inglewood-2', 'e-and-j-seafood-inglewood-2', 'yangmani-los-angeles-2', 'family-fish-market-inglewood', 'fishermans-outlet-los-angeles', 'fishbone-express-gardena-gardena', 'flavors-from-afar-los-angeles-2', 'flowerboy-project-los-angeles', 'fourfortyfour-catering-and-curation-los-angeles', 'freaky-fruit-pizza-los-angeles', 'fresh-and-meaty-burgers-los-angeles-4', 'fresh-ethiopian-restaurant-inglewood', 'fun-diggity-funnel-cakes-los-angeles', 'funculo-los-angeles-2', 'fyrebird-gardena', 'georgias-restaurant-long-beach', 'grams-mission-bbq-riverside', 'grannys-kitchen-los-angeles', 'grilled-fraiche-hyde-park-los-angeles', 'halls-krispy-krunchy-chicken-los-angeles', 'hambones-bar-and-grill-bellflower', 'handys-smoke-house-meats-and-delicacies-long-beach', 'harold-and-belles-los-angeles-5', 'harriets-cheesecakes-unlimited-inglewood', 'harun-coffee-los-angeles-2', 'hawkins-house-of-burgers-los-angeles', 'hilltop-coffee-and-kitchen-los-angeles', 'hilltops-jamaican-market-and-restaurant-a1-pomona', 'honeys-kettle-fried-chicken-culver-city', 'hot-and-cool-cafe-los-angeles', 'hotville-chicken-los-angeles-2', 'industry-cafe-and-jazz-culver-city', 'island-flavors-caribbean-cuisine-los-angeles-2', 'island-reggae-kitchen-gardena', 'island-to-table-patty-hut-los-angeles', 'j-and-js-bbq-and-fish-pomona', 'j-looneys-long-beach-2', 'jackfruit-cafe-los-angeles', 'jaliz-cuisine-of-east-africa-van-nuys-2', 'jamafo-jamaican-food-xpress-los-angeles', 'jamz-creamery-inglewood', 'janga-by-derricks-jamaican-cuisine-culver-city', 'jay-bees-bar-b-q-gardena-3', 'jordans-hot-dogs-los-angeles-2', 'jrs-barbeque-culver-city', 'juice-c-juice-carson-2', 'just-turkey-los-angeles-2', 'karubas-yardy-kitchen-inglewood-2', 'keiths-kettle-corn-azusa', 'kens-ice-cream-parlor-carson', 'kennys-q-bar-b-que-and-more-inglewood', 'king-kone-ice-cream-los-angeles', 'kings-deli-burbank', 'la-buns-downey', 'l-a-grind-coffee-and-tea-bar-los-angeles-2', 'la-louisanne-los-angeles-3', 'ladie-kakes-long-beach-2', 'lalibela-ethiopian-restaurant-los-angeles', 'larayias-bodega-los-angeles', 'l√™berry-bakery-and-donut-pasadena-2', 'lee-esthers-creole-and-cajun-cooking-palmdale', 'lees-caribbean-restaurant-inglewood', 'lees-market-los-angeles-2', 'les-sisters-southern-kitchen-and-bbq-chatsworth', 'lettuce-feast-los-angeles-2', 'little-amsterdam-coffee-shop-los-angeles', 'little-belize-restaurant-inglewood-2', 'little-kingston-jamaican-restaurant-los-angeles', 'the-little-red-hen-coffee-shop-altadena', 'lotus-vegan-north-hollywood', 'lou-the-french-on-the-block-burbank-2', 'louisiana-charlies-long-beach', 'm-and-t-donuts-los-angeles', 'mdears-bakery-and-bistro-los-angeles', 'mack-and-jane-los-angeles', 'main-kitchen-cafe-granada-hills', 'mamas-chicken-and-market-los-angeles', 'mars-caribbean-gardens-gardena-3', 'mardi-gras-tuesday-sherman-oaks', 'matthews-home-style-cooking-gardena-3', 'meals-by-genet-los-angeles', 'mels-fish-shack-los-angeles', 'melkam-ethiopian-restaurant-los-angeles', 'merkato-ethiopian-restaurant-and-market-los-angeles', 'messob-ethiopian-restaurant-los-angeles', 'milk-brookies-los-angeles-4', 'mingles-tea-bar-inglewood-2', 'mo-better-burgers-south-bay-hawthorne', 'moms-burgers-compton', 'moms-haus-van-nuys', 'mr-fries-man-gardena-2', 'ms-bs-m-and-ms-soul-food-inglewood', 'el-chato-taco-truck-los-angeles-2', 'munchies-vegan-diner-santa-ana', 'my-fish-stop-sherman-oaks', 'my-place-cafe-pasadena', 'my-two-cents-los-angeles-3', 'natraliart-jamaican-restaurant-and-market-los-angeles', 'nimbus-coffee-los-angeles-2', 'nitas-corn-and-nacho-southern-california-9', 'nkechi-african-cafe-inglewood', 'o-nells-comfort-kitchen-long-beach', 'obet-and-dels-coffee-los-angeles', 'oh-my-burger-gardena-3', 'one876-caribbean-restaurant-chatsworth', 'onil-chibas-events-pasadena', 'orleans-and-york-deli-los-angeles-3', 'papa-johns-pizza-los-angeles-20', 'park-bench-grill-altadena-2', 'parrains-soulfood-paramount', 'pasadena-fish-market-pasadena', 'patria-coffee-roasters-compton-2', 'peppers-jamaican-belizean-cuisine-los-angeles', 'perrys-joint-pasadena', 'phat-and-juicy-burgers-inglewood', 'phat-birds-los-angeles-6', 'phat-daddys-los-angeles-3', 'phillips-bar-b-que-inglewood-5', 'pizza-of-venice-altadena-2', 'pop-belli-deli-gardena-2', 'popcornopolis-universal-city', 'poppy-rose-los-angeles', 'post-and-beam-los-angeles', 'pucker-up-lemonade-company-compton', 'queen-of-sheba-ethiopian-restaurant-inglewood', 'r-and-r-soul-food-restaurant-carson', 'r-kitchen-soul-food-lakewood', 'rahel-ethiopian-vegan-cuisine-los-angeles', 'ranch-side-cafe-sylmar', 'reds-flavor-table-breakfast-take-out-inglewood', 'revolutionario-north-african-tacos-los-angeles', 'ribtown-b-b-q-los-angeles', 'robert-earls-bbq-long-beach', 'rosalinds-ethiopian-restaurant-los-angeles', 'roscoes-house-of-chicken-and-waffles-los-angeles', 'royal-gourmet-cookies-long-beach', 'rusty-pot-cafe-inglewood', 'sals-gumbo-shack-long-beach', 'sattdown-jamaican-grill-studio-city', 'savage-tacos-truck-los-angeles', 'say-cheese-los-angeles', 'scv-fish-market-santa-clarita-2', 'shaquille-s-los-angeles', 'silverback-coffee-of-rwanda-los-angeles-3', 'simply-d-licious-los-angeles', 'simply-wholesome-los-angeles', 'sip-and-sonder-inglewood', 'skys-gourmet-tacos-los-angeles', 'soul-food-renaissance-long-beach', 'south-la-cafe-los-angeles', 'southern-girl-desserts-los-angeles-2', 'stevies-creole-cafe-los-angeles', 'str8-up-tacos-la-palma-3', 'stuff-i-eat-inglewood', 'sugar-and-spice-ice-cream-los-angeles', 'sugarjones-los-angeles', 'sumptuous-african-restaurant-inglewood', 'sweet-blessings-by-cyler-los-angeles', 'sweet-red-peach-inglewood-2', 'swift-cafe-los-angeles', 't-and-t-lifestyle-los-angeles', 'taco-bar-los-angeles-2', 'taco-mell-catering-los-angeles-2', 'tacos-negros-los-angeles', 'tanjee-bakes-long-beach', 'the-original-texas-barbecue-king-los-angeles-2', 'blvd-kitchen-los-angeles', 'the-boujie-crab-long-beach', 'the-corner-10th-s-bbq-long-beach', 'the-court-cafe-los-angeles', 'the-dw-cookie-co-santa-clarita-2', 'the-gourmet-cobbler-factory-pasadena', 'the-jerk-spot-jamaican-restaurant-culver-city-2', 'the-juice-los-angeles', 'the-original-coley-s-los-angeles', 'the-real-cake-baker-los-angeles-2', 'the-reverse-orangutan-glendora', 'the-sammiche-shoppe-inglewood', 'the-serving-spoon-inglewood', 'soul-food-shack-gardena', 'vtree-at-yamashiro-hollywood', 'the-wood-urban-kitchen-and-sports-lounge-inglewood', 'time-2-grub-lancaster-4', 'tisket-a-tasket-catering-and-food-services-los-angeles', 'totos-african-cuisine-van-nuys', 'treme-kitchen-leimert-park', 'trencher-los-angeles-2', 'twins-smoke-house-bbq-long-beach', 'uedf-fish-and-chips-altadena', 'uncle-andres-bbq-studio-city', 'undergrind-cafe-los-angeles', 'union-pasadena', 'vanillablack-los-angeles', 'veronicas-kitchen-inglewood', 'voodoo-vegan-los-angeles', 'vurger-guyz-los-angeles', 'watts-burgers-los-angeles', 'watts-coffee-house-los-angeles', 'we-cupcake-inglewood', 'whos-hungry-caribbean-restaurant-los-angeles', 'wi-jammin-caribbean-cafe-los-angeles', 'wilsons-bbq-rib-shack-alhambra-2', 'wingopolis-inglewood', 'wings-and-pot-los-angeles', 'wood-spoon-los-angeles-5', 'woodys-bar-b-que-los-angeles', 'worldwide-tacos-los-angeles', 'wowos-smokin-hot-bbq-whittier-2', 'yo-way-eatery-gardena-2', 'yordanos-ethiopian-restaurant-los-angeles', 'your-bakery-1st-inglewood']

    # Chicago: ['ina mae', 'peachs restaurant', 'batter and berries', '14 parish chicago', 'aint she sweet cafe', 'andysunflower cafe', 'banis beets']
    # Detroit: ['seasoned vegan', 'safari', 'silvana', 'sisters carribean cuisine', 'sugar hill creamery', 'fyahbun creative', 'jasmines carribean cuisine', 'le prive', 'meske']
    # hyphenated_restaurants = hyphenate(restaurants)
    non_valid = get_reviews(restaurants, 'detroit')
    print(f"not valid restaurants: {non_valid}")
    print('done')

if __name__ == '__main__':
    main()

