# Telegraph Scraper

A versatile tool for scraping Telegraph pages and collecting data.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
- [Options](#options)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Getting Started

Telegraph Scraper allows you to easily scrape Telegraph pages and collect various types of data. To get started, follow the instructions below.

### Prerequisites

Make sure you have Python 3 installed on your system. You can download Python from [here](https://www.python.org/downloads/).

### Installation

You can install Telegraph Scraper using pip:

```bash
pip install telegraph-scraper
```

To update Telegraph Scraper to the latest version, run:

```bash
pip install telegraph-scraper --upgrade
```

## Usage

### Basic Usage

To scrape a single Telegraph page, use the following command:

```bash
telegraph-scraper <query>
```

Replace `<query>` with your search query. The scraped data will be saved in the current directory.

### Advanced Usage

Telegraph Scraper offers various options for customizing your scraping process. Here are some examples:

- To scrape images from indexed pages:
  ```bash
  telegraph-scraper <query> --images
  ```

- To scrape text from indexed pages:
  ```bash
  telegraph-scraper <query> --text
  ```

- To scrape links from indexed pages:
  ```bash
  telegraph-scraper <query> --links
  ```

- To set a minimum and maximum text length for filtering pages:
  ```bash
  telegraph-scraper <query> --min <min_length> --max <max_length>
  ```

- To scrape multiple queries from a text file:
  ```bash
  telegraph-scraper <input_file> --multiple
  ```

- To scrape multiple queries and download journals and collections:
  ```bash
  telegraph-scraper <input_file> --all
  ```

- To enable caching for changing usernames:
  ```bash
  telegraph-scraper <query> --cacheHit
  ```

- To download media only once per query per user:
  ```bash
  telegraph-scraper <query> --latest
  ```

Explore more options using the `--help` command.

## Options

| Option              | Description                                                          |
| ------------------- | -------------------------------------------------------------------- |
| `--images`          | Scrape images from indexed pages.                                    |
| `--text`            | Scrape text from indexed pages.                                      |
| `--links`           | Scrape links from indexed pages.                                     |
| `--min`             | Set the minimum text length for filtering pages.                     |
| `--max`             | Set the maximum text length for filtering pages.                     |
| `--multiple`        | Scrape multiple queries from a text file.                            |
| `--all`             | Scrape multiple queries and download journals and collections.       |
| `--cacheHit`        | Enable caching for changing usernames.                                |
| `--latest`          | Download media only once per query per user.                          |

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
