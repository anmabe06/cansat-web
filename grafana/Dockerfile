FROM grafana/grafana:8.5.9

ENV GF_ANALYTICS_REPORTING_ENABLED=FALSE \
    GF_AUTH_ANONYMOUS_ENABLED=false \
    GF_AUTH_BASIC_ENABLED=false \
    GF_PATHS_PLUGINS="/var/lib/grafana-plugins" \
    GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=pr0ps-trackmap-panel \
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

COPY datasource.yaml /etc/grafana/provisioning/datasources/
COPY dashboards.yaml /etc/grafana/provisioning/dashboards/
COPY missioncontrol.json /dashboards/
COPY defaults.ini /usr/share/grafana/conf/defaults.ini

EXPOSE 3000
