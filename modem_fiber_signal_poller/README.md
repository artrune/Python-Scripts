# Fiber signal poller
Polls the optic fiber value in dBm from modem/router combo

Uses selenium and chrome driver to scrape my ISP (Telmex) modem website to see the measured fiber signal value reported by the modem, as i had some outages in the past.
Uses influxDB 1.8 to store the time series data.
