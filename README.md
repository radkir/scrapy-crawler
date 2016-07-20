#Crawler for site quoka.de

Crawler extracts property objects from a segment of the site quoka.de:
http://www.quoka.de/immobilien/bueros­gewerbeflaechen/
While crawling, site's filters are used
It's worth noting, that without city filter resulting amount of extracted objects is about 5000, however with this filter on amount is decreased to about 1500. That happens because list of cities, which are given by site as possible filters, lacks cities with small amount of offers, leading them to beeing cut off from crawling result.

Result is transformed to expected format and saved in result.db


