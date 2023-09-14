# Telegraph Scraper

A versatile tool for scraping Telegraph pages and collecting data.

## Getting Started

Usage and installation of telegraph-scraper

### Installation

You can install Telegraph Scraper using pip:

```
$ pip install telegraph-scraper
```

To update Telegraph Scraper to the latest version, run:

```
$ pip install telegraph-scraper --upgrade
```

## Usage

### Basic Usage

To scrape a single Telegraph page, use the following command:

```
$ telegraph-scraper <query>
```

Replace `<query>` with your search query. The scraped data will be saved in the current directory.

### Advanced Usage

Telegraph Scraper offers various options for customizing your scraping process. Here are some examples:

- To scrape images from indexed pages:
  ```
  $ telegraph-scraper <query> --images
  ```

- To scrape text from indexed pages:
  ```
  $ telegraph-scraper <query> --text
  ```

- To scrape links from indexed pages:
  ```
  $ telegraph-scraper <query> --links
  ```

- To set a minimum and maximum text length for filtering pages:
  ```
  $ telegraph-scraper <query> --min <min_length> --max <max_length>
  ```

Explore more options using the `--help` command.

## Options

| Option               | Secondary Options | Description                                                                                               |
| -------------------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| -i or --input-file   | <INPUT_FILE>      | Text file containing the target list. Ex: list.txt                                                         |
| -o or --output-directory | <OUTPUT_DIRECTORY> | Output directory for query results (default "./Scraper/")                                           |
| -w or --workers      | <WORKERS>         | Number of parallel execution workers (default 4)                                                         |
| -I or --images       |                   | Collect all images on indexed pages                                                                      |
| -T or --text         |                   | Collect all text on indexed pages                                                                        |
| -L or --links        |                   | Collect all links on indexed pages                                                                       |
| -max                 | <MAX>             | Filter pages with text length greater than the defined value.                                            |
| -min                 | <MIN>             | Filter pages with text length less than the defined value.                                               |

## License

This project is licensed under the GPL-3.0 - see the [LICENSE](LICENSE) file for details.
