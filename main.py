import os
from scraper.engine import JobScraper

# Configuration
# You can change these to search for different roles
JOB_TITLE = "Data Analyst"
LOCATION = "Lisboa"


def main():
    print(f"Starting search for {JOB_TITLE} in {LOCATION}...")

    # 1. Initialize the scraper
    bot = JobScraper()

    try:
        # 2. Perform the search automation
        bot.perform_search(JOB_TITLE, LOCATION)

        # 3. Extract the results
        jobs = bot.get_results()

        # 4. Display and Save the results
        if jobs:
            import csv  # Import needed for saving the file

            print(f"\nSuccess! Found {len(jobs)} jobs on this page:")
            print("=" * 50)

            # 4a. Print ALL jobs to the terminal
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job['title']}")
                print(f"   Link: {job['link']}")
                print("-" * 50)

            # 4b. Save ALL jobs to a CSV file
            keys = jobs[0].keys()  # Gets the dictionary keys ('title' and 'link')
            with open('job_results.csv', 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(jobs)

            print(f"\n📊 Process Complete! {len(jobs)} jobs exported to 'job_results.csv'")
        else:
            print("\nNo jobs were extracted. The search might have yielded no results or the page layout changed.")

    except Exception as e:
        print(f"\nAn error occurred during the process: {e}")

    finally:
        # 5. Close the browser
        print("\nClosing browser...")
        bot.quit()
        print("Process complete!")


if __name__ == "__main__":
    main()