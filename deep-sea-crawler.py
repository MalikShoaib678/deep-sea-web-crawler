import threading
import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
import os
import time
import curses

class WebCrawler:
    def __init__(self, scope, output_dir, max_threads, max_depth):
        self.session = requests.Session()
        self.lock = threading.Lock()
        
        self.scope = scope
        self.output_dir = output_dir
        
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.active_threads = 0

        self.urls = []
        self.js_files = []
        self.other_files = []
        self.image_files = []
        
        self.upload_endpoints = []
        self.api_endpoints = []
        self.input_fields = []
        
        self.api_keywords = ['graphql']
        self.unchecked = []
        self.make_screen()
        self.overwrite_check = None
    
    
    def print_on_current_position(self, status, overwrite=False, design=None):
        try:
            with self.lock:
                output = ' ' + status
                # Get the current cursor position
                current_row, current_column = self.stdscr.getyx()
                max_row, max_column = self.stdscr.getmaxyx()
                shading_line = "█" # Shading line character
    
                
                # Print the status at the current cursor position
                if overwrite == False:
                    # Move the cursor to the next line
                    next_row = current_row + 1
                    if next_row == max_row:
                        # Scroll the screen if the next row exceeds the maximum row
                        self.stdscr.scroll(1)
                        next_row = max_row - 1
    
                    if self.overwrite_check == True:
                        self.stdscr.move(current_row, 0)
                        self.stdscr.clrtoeol()  # Clear the current line
                        self.stdscr.addstr(current_row, 0, shading_line, curses.color_pair(2))  # Add shading line
                        if design:
                            self.stdscr.addstr(current_row, 1, output, design)  # Print the status after the shading line
                        else:
                            self.stdscr.addstr(current_row, 1, output)  # Print the status after the shading line
                    else:
                        self.stdscr.move(next_row, 0)
                        self.stdscr.clrtoeol()  # Clear the current line
                        if design:
                            self.stdscr.addstr(current_row, 1, output, design)  # Print the status after the shading line
                        else:
                            self.stdscr.addstr(current_row, 1, output)  
                            
                    self.overwrite_check = False
                elif overwrite == True:
                    self.stdscr.move(current_row, 0)
                    self.stdscr.clrtoeol()  # Clear the current line
                    self.stdscr.addstr(current_row, 0, shading_line)  # Add shading line
                    if design:
                        self.stdscr.addstr(current_row, 1, output, design)  # Print the status after the shading line
                    else:
                        self.stdscr.addstr(current_row, 1, output)  # Print the status after the shading line
                    self.overwrite_check = True
    
                # Refresh the screen to display the changes
                self.stdscr.refresh()
        except:
            self.make_screen()
        
    def make_screen(self):
        # Initialize curses
        self.stdscr = curses.initscr()
        
        # Set up color pairs
        curses.start_color()
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_CYAN) # for others
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_CYAN) # For overwrite=True
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK) #For JS

        # Set the font
        #self.stdscr.attron(curses.A_BOLD)
        
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        
    def cleanup(self):
        # Cleanup curses
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
            
    def spidy(self, url=None, depth=0):
        try:
            if 'http://' not in url and 'https://' not in url:
                url = 'http://' + url
            response = self.session.get(url, timeout=5)  # Add a timeout of 5 seconds
            parsed_response = BeautifulSoup(response.content, 'html.parser')
            elements = parsed_response.findAll('a')
            threads = []
    
            self.extract_files(url, response.text)  # Call the method to extract and save file URLs from the response
            for element in elements:
                link2 = element.get('href')
                if link2:
                    link = urllib.parse.urljoin(url, link2)
                    parsed_link = urllib.parse.urlparse(link)
                    if '#' in parsed_link.path:
                        link = link.split('#')[0]
                    if parsed_link.netloc and 'logout' not in link and parsed_link.netloc in self.scope and (link not in self.urls or link in self.unchecked):
                        if link.endswith('.js'):
                            if link not in self.js_files:
                                self.lock.acquire()
                                self.js_files.append(link)
                                self.lock.release()
                                self.save_crawled_files('jsfiles.txt', link)
                        else:
                            self.urls.append(link)
                            self.save_crawled_files('urls.txt', link)
                            
                            status = f"Crawled::URLs:{len(self.urls)}|unchecked:{len(self.unchecked)}||Images:{len(self.image_files)}|JS:{len(self.js_files)}||input-fields:{len(self.input_fields)}|XML&Jsons:{len(self.other_files)}||file-upload:{len(self.upload_endpoints)}|api:{len(self.api_endpoints)}||Threads:{self.active_threads}"
                            self.print_on_current_position(status, True, curses.color_pair(3) | curses.A_BOLD)
                            if depth <= self.max_depth and self.active_threads < self.max_threads:
                                # Create a new thread and start it
                                thread = threading.Thread(target=self.spidy, args=(link, depth + 1))
                                thread.start()
                                threads.append(thread)
                                self.active_threads += 1
                                if url in self.unchecked:
                                    self.unchecked.remove((url, depth))
                            else:
                                if (link, depth + 1) not in self.unchecked:
                                    if depth + 1 <= self.max_depth:
                                        self.unchecked.append((link, depth + 1))
    
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
                self.active_threads -= 1
    
        except requests.exceptions.RequestException as e:
            self.print_on_current_position(f"An error occurred while crawling {url}: {e}")
        #finally:
            #self.stdscr.clear()
            #self.cleanup() 

    def run(self):
        for url in self.scope:
            self.spidy(url)
    
        while len(self.unchecked) != 0:
            threads = []
            urls_to_check = self.unchecked[:min(self.max_threads - self.active_threads, len(self.unchecked))]
            self.unchecked = self.unchecked[min(self.max_threads - self.active_threads, len(self.unchecked)):]
    
            for url, depth in urls_to_check:
                thread = threading.Thread(target=self.spidy, args=(url, depth))
                thread.start()
                threads.append(thread)
                self.active_threads += 1
    
            for thread in threads:
                thread.join()
                self.active_threads -= 1
        time.sleep(5)
        self.cleanup()
        print(f"SCAN COMPLETED: urls:{len(self.urls)} | jsfiles:{len(self.js_files)} | otherfiles:{len(self.other_files)} | images:{len(self.image_files)}")
        
    def extract_files(self, url, response_text):
        parsed_response = BeautifulSoup(response_text, 'html.parser')
    
        # Extract JS files
        js_scripts = parsed_response.findAll('script', src=True)
        
        for script in js_scripts:
            link = script['src']
            if '://' not in link:
                link = urllib.parse.urljoin(url, link)
            if link:
                if any(domain in link for domain in self.scope):  # Check if at least one domain from self.scope is present in link
                    if link not in self.js_files:
                        self.lock.acquire()
                        self.js_files.append(link)
                        self.lock.release()
                        self.save_crawled_files('jsfiles.txt', link)
                        self.print_on_current_position(f"Crawled JS: {len(self.js_files)} |Endpoint: {script['src']} ", False, curses.color_pair(4))  # #self.print_on_current_position the number of crawled JS files, number of active threads, and the JS file
    
        # Extract other files (XML, JSON, etc.)
        other_files = parsed_response.findAll(['link', 'script'], href=True)
        for file_element in other_files:
            link = file_element['href']
            if '://' not in link:
                link = urllib.parse.urljoin(url, link)
    
            if link:
                if any(domain in link for domain in self.scope):  # Check if at least one domain from self.scope is present in link
                    if link.endswith(('.xml', '.json')):  # Add the desired file extensions to check
                        if link not in self.other_files:
                            self.lock.acquire()
                            self.other_files.append(link)
                            self.lock.release()
                            file_extension = link.split('.')[-1]
                            self.save_crawled_files(f'{file_extension}s.txt', link)
                            self.print_on_current_position(f"Crawled {file_extension.upper()} files: {len(self.other_files)} | File: {link}", False, curses.color_pair(2))
    
        # Extract image files
        image_elements = parsed_response.findAll('img', src=True)
        for image_element in image_elements:
            link = image_element['src']
            if '://' not in link:
                link = urllib.parse.urljoin(url, link)
    
            if link:
                if any(domain in link for domain in self.scope):  # Check if at least one domain from self.scope is present in link
                    if link not in self.image_files:
                        self.lock.acquire()
                        self.image_files.append(link)
                        self.lock.release()
                        self.save_crawled_files('image_files.txt', link)
                        #self.print_on_current_position(f"Crawled image files: {len(self.image_files)} | Threads: {self.active_threads} | Image file: {link}")
        # Find file upload endpoints
        form_elements = parsed_response.findAll('form')
        for form in form_elements:
            input_elements = parsed_response.findAll('input')
            action = form.get('action')
            if 'upload' in form:
                upload_endpoint = urllib.parse.urljoin(url, action)
                if upload_endpoint not in self.upload_endpoint:
                    self.upload_endpoint.append(upload_endpoint)
                    if any(domain in upload_endpoint for domain in self.scope):
                        file_name = 'upload-endpoints.txt'
                        self.lock.acquire()
                        self.save_crawled_files(file_name, upload_endpoint)
                        self.lock.release()
                        self.print_on_current_position(f"[{len(self.upload_endpoint)}]Crawled upload_endpoint: {upload_endpoint}", False, curses.color_pair(2))
            else:
                for input_element in input_elements:
                    input_type = input_element.get('type')
                    if input_type == 'file':
                        upload_endpoint = urllib.parse.urljoin(url, action)
                        if upload_endpoint not in self.upload_endpoint:
                            self.upload_endpoint.append(upload_endpoint)
                            if any(domain in upload_endpoint for domain in self.scope):
                                file_name = 'upload-endpoints.txt'
                                self.lock.acquire()
                                self.save_crawled_files(file_name, upload_endpoint)
                                self.lock.release()
                                self.print_on_current_position(f"[{len(self.upload_endpoint)}]Crawled upload_endpoint: {upload_endpoint}",  False, curses.color_pair(2))
                                
                
                    
        # Find input fields
        if url not in self.input_fields:
            name = None
            input_elements = parsed_response.findAll('input')
            for input_element in input_elements:
                input_type = input_element.get('type')
                if input_type:
                    name = input_element.get('name')
                    if name:
                        file_name = f'{input_type}-input-fields.txt'
                        self.lock.acquire()
                        self.save_crawled_files(file_name, url)
                        self.input_fields.append(url)
                        self.lock.release()
                        #self.print_on_current_position(f"Found input field: {name}")
                        
        if url not in self.api_endpoints:
            if any(word in response_text or word in url for word in self.api_endpoints):
                for word in self.api_keywords:
                    self.lock.acquire()
                    self.api_endpoints.append(url)
                    file_name = f'{word}-api-endpoints.txt'
                    self.save_crawled_files(file_name, url)
                    self.lock.release()
                    self.print_on_current_position(f"Found {word} api-endpoint: {url}",  False, curses.color_pair(2))
                                    
    def save_crawled_files(self, file_name, link):
        output_path = os.path.join(self.output_dir, file_name)
        with open(output_path, 'a') as f:
            f.write(f'{link}\n')

   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Crawler')
    parser.add_argument('-f', '--file', type=str, help='Path to file containing subdomains', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output directory name', default='result')
    parser.add_argument('-t', '--max_threads', type=int, default=10, help='Maximum number of threads')
    parser.add_argument('-d', '--max_depth', type=int, default=3, help='Maximum crawling depth')
    args = parser.parse_args()

    # Read subdomains from file
    scope = []
    with open(args.file, 'r') as f:
        scope = [line.strip() for line in f]

    # Create the output directory
    os.makedirs(args.output, exist_ok=True)

    # Create files in the output directory
    files_to_create = ['jsfiles.txt', 'urls.txt', 'xmls.txt', 'jsons.txt', 'image_files.txt']  # Add the desired file extensions to create
    for file_name in files_to_create:
        file_path = os.path.join(args.output, file_name)
        with open(file_path, 'w') as f:
            f.write('')

    # Example usage
    crawler = WebCrawler(scope=scope, output_dir=args.output, max_threads=args.max_threads, max_depth=args.max_depth)
    crawler.run()
    
