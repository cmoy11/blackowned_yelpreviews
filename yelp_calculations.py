import csv
import os
import re
import random
import sqlite3

from regex import A

def clean_csvs(city):
    # loops through folder and gathers list of uncleaned review csv files
    directory = f'{city}/review_csvs'
    csv_files = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            csv_files.append(f)

    for file in csv_files:
        print(file)
        if file == f'{city}/review_csvs/.DS_Store':
            continue
        # reads all data from each file
        with open(file, newline='\n') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            data = []
            restaurant_name = file.replace(f'{city}/review_csvs/', '').replace('-', ' ').replace('.csv', '')

            # creates csv reader object and loops through each reveiw for the restaurant
            # initializes an empty list that will be used to check for duplicate values
            all_reviews = []
            for row in reader:
                date=row[0]

                # three regex strings that will be used to get date
                regex = r"(\d{1,2})\/\d{1,2}\/\d{4}"
                regex2 = r"\d{1,2}\/(\d{1,2})\/\d{4}"
                regex3 = r"\d{1,2}\/\d{1,2}\/(\d{4})"

                # loops through csv reader and gets date information
                month = re.findall(regex, date)
                day = re.findall(regex2, date)
                year = re.findall(regex3, date)

                # converts dates into sortable format
                if len(month[0]) == 1:
                    month[0] = '0' + month[0]
                if len(day[0]) == 1:
                    day[0] = '0' + day[0]

                new_date = year[0] + month[0] + day[0]

                star = row[1][0]
                review = row[2]
                if review in all_reviews:
                    continue
                else:
                    all_reviews.append(review)

                # creates data list for each review
                review_list = [date, int(new_date), int(star), review.replace('¬†', '').replace(' \xa0', ' ')]
                
                # appends review list to both local (restaurant only) and global (complete) lists of reviews
                data.append(review_list)

            # sorts reviews based on date
            sorted_data = sorted(data, key = lambda x:x[1])
            sum = 0
            count = 0
            averaged_data = []

            # creates running average for reviews
            for row in sorted_data:
                date = row[0]
                converted_date = row[1]
                rating = row[2]
                review = row[3]

                sum += rating
                count += 1

                average = round(sum/count, 2)
                averaged_data.append([date, converted_date, rating, average, review])

            # writes csv file with averaged value for each restaurant
            filename = f'{city}/cleaned_csvs/' + restaurant_name.replace(' ', '_') + '_cleaned.csv'
            with open(filename, "w") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["date", "converted_date", "rating", "average", "review"])
                for row in averaged_data:
                    csvwriter.writerow(row)

def get_tdata(city):
    directory = f'{city}/cleaned_csvs'
    csv_files = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            csv_files.append(f)

    all_restaurants =  []
    num_reviews = 0
    for file in csv_files:
        print(file)
        if file == f'{city}/cleaned_csvs/.DS_Store':
            continue
        with open(file, newline='\n') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            restaurant_name = file.replace(f'{city}/cleaned_csvs/', '').replace('_', ' ').replace(' cleaned.csv', '')

            counter = 0
            num_20200518 = -1
            average_20200518 = -1
            num_20200618 = -1
            average_20200618 = -1
            num_20200718 = -1
            average_20200718 = -1
            num_20200918 = -1
            average_20200918 = -1
            num_20201218 = -1
            average_20201218 = -1
            num_20210618 = -1
            average_20210618 = -1

            for row in reader:
                converted_date = int(row[1])
                num_reviews += 1

                if counter == 0:
                    initial_date = converted_date
                    if initial_date > 20200518:
                        num_20200518 = 0
                        average_20200518 = 0
                    if initial_date > 20200618:
                        num_20200618 = 0
                        average_20200618 = 0
                    if initial_date > 20200718:
                        num_20200718 = 0
                        average_20200718 = 0
                    if initial_date > 20200918:
                        num_20200918 = 0
                        average_20200918 = 0
                    if initial_date > 20201218:
                        num_20201218 = 0
                        average_20201218 = 0
                    if initial_date > 20210618:
                        num_20210618 = 0
                        average_20210618 = 0

                if converted_date >= 20200518 and num_20200518 == -1:
                    num_20200518 = counter
                    average_20200518 = last_average
                if converted_date >= 20200618 and num_20200618 == -1:
                    num_20200618 = counter
                    average_20200618 = last_average
                if converted_date >= 20200718 and num_20200718 == -1:
                    num_20200718 = counter
                    average_20200718 = last_average
                if converted_date >= 20200918 and num_20200918 == -1:
                    num_20200918 = counter
                    average_20200918 = last_average
                if converted_date >= 20201218 and num_20201218 == -1:
                    num_20201218 = counter
                    average_20201218 = last_average
                if converted_date >= 20210618 and num_20210618 == -1:
                    num_20210618 = counter
                    average_20210618 = last_average

                last_average = float(row[3])
                counter += 1
            l = [restaurant_name, num_20200518, average_20200518, num_20200618, average_20200618, num_20200718, average_20200718, num_20200918, average_20200918, num_20201218, average_20201218, num_20210618, average_20210618]

            try:
                idx = l.index(-1)
            except:
                idx = 0
                new_l = l
            if idx == 1:
                new_l = []
                for x in l:
                    if x == -1:
                        new_l.append(0)
                    else: 
                        new_l.append(x)
            elif idx != 0:
                num = l[idx-2]
                average = l[idx-1]

                counter = 0
                new_l = []
                for x in l:
                    if x == -1 and counter%2 == 1:
                        new_l.append(num)
                    elif x==-1 and counter%2 == 0: 
                        new_l.append(average)
                    else:
                        new_l.append(x)
                    counter += 1
            all_restaurants.append(new_l)

    filename = f'tdata/{city}' + '_tdata.csv'
    with open(filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['restaurant_name', 'num_20200518', 'average_20200518', 'num_20200618', 'average_20200618', 'num_20200718', 'average_20200718', 'num_20200918', 'average_20200918', 'num_20201218', 'average_20201218', 'num_20210618', 'average_20210618'])
        for row in all_restaurants:
            csvwriter.writerow(row)
    
    print(num_reviews)

def create_database():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/not_black_owned_reviews.db')
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS allReviews
        (objectID INTEGER PRIMARY KEY, city STRING, yelpAlias STRING, date STRING, convertedDate INTEGER, rating INTEGER, review STRING)
        """
    )
    conn.commit()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS City
        (ID INTEGER PRIMARY KEY, city STRING)
        """
    )
    conn.commit()

    city_dict = {0:"detroit", 1:"los angeles"}
    for key in city_dict:
        cur.execute(
            """
            INSERT OR IGNORE INTO City (ID, city)
            VALUES (?, ?)
            """, (key, city_dict[key])
        )
        conn.commit()
    
    return cur, conn

def populate_reviews(cur, conn, folderpath, city, id):
    directory = f'{folderpath}/cleaned_csvs'
    csv_files = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            csv_files.append(f)

    all_reviews =  []
    num_reviews = 0
    for file in csv_files:
        print(file)
        if file == f'{folderpath}/cleaned_csvs/.DS_Store':
            continue
        with open(file, newline='\n') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            yelp_alias = file.replace(f'{folderpath}/cleaned_csvs/', '').replace('_', '-').replace('-cleaned.csv', '')

            for row in reader:
                num_reviews += 1
                date = row[0]
                converted_date = row[1]
                rating = row[2]
                review = row[4]
                
                cur.execute(
            """
            INSERT OR IGNORE INTO allReviews (objectID, city, yelpAlias, date, convertedDate, rating, review)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id + str(num_reviews), city, yelp_alias, date, converted_date, rating, review)
        )
        conn.commit()

def main():
    clean_csvs('detroit/not-black-owned')
    get_tdata('detroit/not-black-owned') 
    cur, conn = create_database()
    populate_reviews(cur, conn, 'detroit/not-black-owned', "0", "1000")
    print('done')

if __name__ == '__main__':
    main()