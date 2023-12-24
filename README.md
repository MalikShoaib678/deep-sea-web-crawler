
```markdown
# 🌐 Web Crawler

This script is a powerful 🕷️ web crawler designed to scan and analyze subdomains. It efficiently crawls through websites, providing valuable insights and information.

## Usage

To use the script, follow these steps:

1. Ensure you have the necessary libraries installed:
   - `threading`
   - `requests`
   - `bs4` from `BeautifulSoup`
   - `urllib.parse`
   - `argparse`
   - `os`
   - `time`
   - `curses`

2. Clone the repository and navigate to the script's directory.
    git clone https://github.com/MalikShoaib678/deep-sea-crawler.git
    cd deep-sea-crawler
3. Provide input by creating a file with the target subdomains. For example:
   ```
   echo 'testphp.vulnweb.com' > target.txt
   ````

4. Execute the command below to start the scan:
   ```
   python3 deep-sea-crawler.py --file target.txt --max_threads 40 --max_depth 3
   ````

## Results

After the scan is completed, the script generates an output directory (default name: "result") where the results are stored. The following files are created:

- 🗄️ `hidden-input-fields.txt`: Contains hidden input fields found in the crawled pages.
- 🖼️ `image_files.txt`: Lists the image files discovered during the crawling process.
- 📜 `jsfiles.txt`: Lists the JavaScript files found.
- 📋 `jsons.txt`: Lists the JSON files encountered.
- 🔐 `password-input-fields.txt`: Contains password input fields found in the scanned pages.
- 📥 `submit-input-fields.txt`: Lists submit input fields discovered.
- ✏️ `text-input-fields.txt`: Contains text input fields found.
- 🔗 `urls.txt`: Lists the URLs encountered during the crawling process.
- 📄 `xmls.txt`: Lists the XML files encountered.

The script also provides a summary of the scan, displaying the count of URLs, JavaScript files, other files, and images discovered.

To get the line count of each result file, navigate to the output directory(default 'result') and use the following command:
```
wc -l *
```

## Note

This script is intended for professional use and should be used responsibly. Ensure that you have the necessary permissions before scanning any websites. Additionally, this README provides a brief overview of the script's functionality and not an exhaustive guide.

Feel free to contribute to this open-source project by submitting bug reports, feature requests, or pull requests. Your feedback is highly appreciated!

Enjoy exploring the depths of the web with the Web Crawler! 🌊🔍
```

