FROM grafana/grafana:8.5.9

ENV GF_ANALYTICS_REPORTING_ENABLED=FALSE \
    GF_AUTH_ANONYMOUS_ENABLED=false \
    GF_AUTH_BASIC_ENABLED=false \
    GF_PATHS_PLUGINS="/var/lib/grafana-plugins" \
    GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=ryantxu-ajax-panel \
    # GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=pr0ps-trackmap-panel \
    # GF_INSTALL_PLUGINS="https://github.com/anmabe06/3d-asset-rotator-grafana-plugin/archive/refs/heads/master.zip;my-grafana-plugin" \
    GF_SECURITY_ADMIN_PASSWORD=admin \
    GF_SECURITY_ADMIN_USER=admin \
    GF_SECURITY_ALLOW_EMBEDDING=true \
    GF_SECURITY_DISABLE_GRAVATAR=true \
    GF_USERS_ALLOW_SIGN_UP=false \
    GF_ANALYTICS_REPORTING_ENABLED=FALSE \
    DATABASE_PORT=3306

USER root

RUN mkdir -p "$GF_PATHS_PLUGINS" && \
    chown -R grafana "$GF_PATHS_PLUGINS"

USER grafana

RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install pr0ps-trackmap-panel 2.1.2
RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install innius-video-panel 1.0.5
RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install grafana-xyzchart-panel
RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install satellogic-3d-globe-panel
RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" --pluginUrl https://github.com/ryantxu/ajax-panel/releases/download/v0.0.6/ryantxu-ajax-panel-0.0.6.zip plugins install ryantxu-ajax-panel 0.0.6
# RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ryantxu-ajax-panel

#### INSTALL FROM WEB ADRESS
#### RUN grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" --pluginUrl https://grafana.com/api/plugins/blackcowmoo-googleanalytics-datasource/versions/0.1.4/download plugins install blackcowmoo-googleanalytics-datasource
# RUN wget "https://github.com/ilgizar/ilgizar-candlestick-panel/archive/refs/heads/master.zip"
# RUN unzip "../master.zip" -d "${GF_PATHS_PLUGINS}/ilgizar-candlestick-panel"
# RUN grafana-cli --repo "https://github.com/ilgizar/ilgizar-candlestick-panel/archive/refs/heads/master.zip" plugins install ilgizar-candlestick-panel



# TODO: COPY plugins.yaml /etc/grafana/provisioning/plugins/
# COPY /grafana-plugins/ "${GF_PATHS_PLUGINS}"
COPY datasource.yaml /etc/grafana/provisioning/datasources/
COPY dashboards.yaml /etc/grafana/provisioning/dashboards/
COPY live_stats.json /dashboards/
COPY time_series_data.json /dashboards/
COPY defaults.ini /usr/share/grafana/conf/defaults.ini

EXPOSE 3000

