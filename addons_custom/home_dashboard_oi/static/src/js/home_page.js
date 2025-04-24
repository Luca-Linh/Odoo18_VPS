/** @odoo-module **/
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { onMounted, Component, useRef, useEffect } from "@odoo/owl";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";

const actionRegistry = registry.category("actions");

export class oHomePage extends Component {
    static template = 'oBoard';
    static props = ["*"];

    // Class properties
    deferredPrompt = null;

    setup() {
        this.effect = useService("effect");
        this.action = useService("action");
        this.orm = useService("orm");

        // State initialization
        this.state = useState({
            dashboards_templates: ['oSideBar', 'oWorkspace'],
            oi_bse: {},
            oi_set: {},
            oi_usd: {},
            templates: [],
            isAdmin: false,
            isDataReady: false,
        });

        // Bind methods
        this.handleCardClick = this.handleCardClick.bind(this);
        this.applyDateFilter = this.applyDateFilter.bind(this);
        this.showInstallPrompt = this.showInstallPrompt.bind(this);
        this.getDtfFromUrl = this.getDtfFromUrl.bind(this);
        this.fetchData = this.fetchData.bind(this);
        this.render_cards = this.render_cards.bind(this);
        this.render_graphs = this.render_graphs.bind(this);
        this.render_lists = this.render_lists.bind(this);
        this.getIconClass = this.getIconClass.bind(this);
        this.getCardClass = this.getCardClass.bind(this);
        this.getFavButtonClass = this.getFavButtonClass.bind(this);
        this.btn_open_favourite = this.btn_open_favourite.bind(this);
        this.btn_setting = this.btn_setting.bind(this);
        this.btn_kpi = this.btn_kpi.bind(this);

        // Lifecycle hooks
        onWillStart(async () => {
            this.isAdmin = await user.hasGroup("base.group_erp_manager");
            const dtf = this.getDtfFromUrl();
            // console.log("Fetched dtf in onWillStart:", dtf);

            // Update state with URL filter
            this.state.oi_set.user_slicer = dtf;
            // console.log("Initialized state.oi_set.user_slicer:", this.state.oi_set.user_slicer);

            await this.fetchData(dtf);
            this.state.isDataReady = true;
        });

        useEffect(
            () => {
                const handleUrlChange = () => {
                    const dtf = this.getDtfFromUrl();
                    // console.log("Fetched dtf form getDtfFromUrl for useEffect:", dtf);

                    if (dtf !== this.state.oi_set.user_slicer) {
                        // console.log("State updated from URL change:", dtf);
                        this.state.oi_set.user_slicer = dtf;
                    }
                };

                handleUrlChange();
            },
            () => [window.location.search] // Watch for URL changes
        );

        onMounted(() => {
            this.title = 'Dashboard';

            const dtf = this.getDtfFromUrl();
            // console.log("Fetched dtf in onMounted:", dtf);

            if (this.render_cards) {
                this.render_cards(dtf);
            } else {
                console.error("render_cards is not defined.");
            }

            if (this.render_graphs) {
                this.render_graphs(dtf);
            } else {
                console.error("render_graphs is not defined.");
            }

            if (this.render_lists) {
                this.render_lists(dtf);
            } else {
                console.error("render_lists is not defined.");
            }

            // Handle PWA installation prompt
            window.addEventListener('beforeinstallprompt', (event) => {
                event.preventDefault();
                this.deferredPrompt = event;

                const installButton = document.getElementById('install-button');
                if (installButton) {
                    installButton.style.display = 'block';
                    installButton.addEventListener('click', () => this.showInstallPrompt());
                }
            });
        });
    }

    // Helper methods
    getDtfFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const dtf = urlParams.get('dtf') || 'cy'; // Default to 'cy'
        // console.log("Fetched dtf from URL:", dtf);
        return dtf;
    }

    async fetchData(filter) {
        try {
            // console.log("Fetching data for filter:", filter);

            // Fetch base data
            const bse_data = await this.orm.call('odi.home.page', 'get_base_data', [filter]);
            this.state.oi_bse = bse_data && typeof bse_data === 'object' ? bse_data : {};

            // Fetch settings data
            const sett_data = await this.orm.call('odi.home.page', 'get_sett_data', [filter]);
            if (sett_data) {
                this.state.oi_set = { ...this.state.oi_set, ...sett_data };
            }

        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }

    // Apply Date Filter ✅
    applyDateFilter(filter) {
        console.log("Applying filter:", filter);

        // Immediately update the UI state
        this.state.oi_set.user_slicer = filter;
        this.render(); // Force a re-render to update the button highlight

        // Update URL with the selected filter
        const url = new URL(window.location);
        url.searchParams.set('dtf', filter);
        window.history.pushState({}, '', url);

        // Fetch data asynchronously
        this.fetchData(filter)
            .then(() => {
                console.log("Data fetched successfully for filter:", filter);
                this.render_cards(filter);
                this.render_graphs(filter);
                this.render_lists(filter);
            })
            .catch((error) => {
                console.error("Error fetching data for filter:", filter, error);
            });
    }


    showInstallPrompt() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            this.deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                } else {
                    console.log('User dismissed the install prompt');
                }
                this.deferredPrompt = null;
            });
        } else {
            console.error('Install prompt is not available.');
        }
    }

    // Card rendering ✅
    async render_cards(filter) {
        try {
            const usr_data = await this.orm.call('odi.home.page', 'get_card_data', [filter]);
            const cardContainer = document.getElementById('cardsContainer');

            if (!cardContainer) {
                console.error('Card container not found.');
                return;
            }

            cardContainer.innerHTML = ''; // Clear previous cards

            if (usr_data) {
                this.state.oi_usd = {}; // Reset state before adding new cards
                const uniqueTiles = new Set(); // Store unique tile identifiers

                Object.keys(usr_data).forEach((key) => {
                    if (key.endsWith('_head') && usr_data[key] !== null) {
                        const tile = key.split('_')[0]; // Extracts '1', '2', etc.
                        if (uniqueTiles.has(tile)) return;
                        uniqueTiles.add(tile);

                        this.state.oi_usd[`${tile}_lab`] = usr_data[key];
                        this.state.oi_usd[`${tile}_val`] = usr_data[`${tile}_count`] || 0;
                        this.state.oi_usd[`${tile}_kpi`] = usr_data[`${tile}_kpi`] || '0.00';
                        this.state.oi_usd[`${tile}_model`] = usr_data[`${tile}_model`] || '';
                        this.state.oi_usd[`${tile}_view_mode`] = usr_data[`${tile}_view_mode`] || '';
                        this.state.oi_usd[`${tile}_views`] = usr_data[`${tile}_views`] || [];
                        this.state.oi_usd[`${tile}_domain`] = usr_data[`${tile}_domain`] || [];
                        this.state.oi_usd[`${tile}_target`] = usr_data[`${tile}_target`] || 'current';
                        this.state.oi_usd[`${tile}_icon`] = usr_data[`${tile}_icon`] || 'fa fa-bar-chart'; // Default icon
                    }
                });

                uniqueTiles.forEach((tile) => {
                    let iconClass = this.state.oi_usd[`${tile}_icon`];

                    if (typeof iconClass !== "string") {
                        console.warn(`Invalid iconClass for tile ${tile}:`, iconClass);
                        iconClass = 'fa fa-bar-chart'; // Default fallback
                    }

                    const cardDiv = document.createElement('div');
                    const cardClass = this.getCardClass();
                    cardDiv.className = `home-card ${cardClass}`.trim();

                    const cardBody = document.createElement('div');
                    cardBody.className = "home-card-body d-flex align-items-center";

                    const iconDiv = document.createElement('div');
                    iconDiv.className = "home-icon";
                    iconDiv.innerHTML = iconClass.startsWith('fa')
                        ? `<i class="${iconClass}"></i>`
                        : `<img src="${iconClass}" alt="icon">`;

                    const contentDiv = document.createElement('div');
                    contentDiv.className = "home-content";

                    // Title and KPI container (stacked vertically)
                    const titleContainer = document.createElement('div');
                    titleContainer.className = "home-title-container";

                    const titleDiv = document.createElement('div');
                    titleDiv.className = "home-title";
                    titleDiv.innerHTML = `<h5>${this.state.oi_usd[`${tile}_lab`]}</h5>`;

                    const kpiDiv = document.createElement('div');
                    kpiDiv.className = "home-kpi";
                    kpiDiv.innerHTML = `<small>${this.state.oi_usd[`${tile}_kpi`] || '0.00'}</small>`;

                    // Append title and KPI (KPI will be below title)
                    titleContainer.appendChild(titleDiv);
                    titleContainer.appendChild(kpiDiv);

                    const valueDiv = document.createElement('div');
                    valueDiv.className = "home-value";
                    valueDiv.innerHTML = `<p>${this.state.oi_usd[`${tile}_val`] || 0}</p>`;

                    contentDiv.appendChild(titleContainer);
                    contentDiv.appendChild(valueDiv);
                    cardBody.appendChild(iconDiv);
                    cardBody.appendChild(contentDiv);
                    cardDiv.appendChild(cardBody);

                    cardDiv.addEventListener('click', this.handleCardClick.bind(this, tile));

                    cardContainer.appendChild(cardDiv);
                });
            }
        } catch (error) {
            console.error("Error rendering cards:", error);
        }
    }

    // Graph rendering ✅
    async render_graphs(filter) {
        const sett_data = await this.orm.call('odi.home.page', 'get_sett_data', [filter]);
        const layout = parseInt(sett_data?.graph_layout || 3, 10); // Ensure layout is a number
        const columnsClass = `col-lg-${12 / layout}`; // Dynamic Bootstrap grid class

        const data = await this.orm.call('odi.home.page', 'get_graphs', [filter]);
        const graphContainer = document.getElementById('graphsContainer');
        if (graphContainer) {
            graphContainer.innerHTML = '';

            data.forEach((graph, index) => {
                const graphId = `graph_${index + 1}_${graph.header.replace(/\s+/g, '_')}`;
                const { values, labels, header, graph_type, graph_colors, graph_legend } = graph;

                const graphDiv = document.createElement('div');
                graphDiv.classList.add('x-card', 'text-color', columnsClass);
                graphDiv.innerHTML = `
                    <div class="x-card-body pb-0">
                        <p class="stat-head" style="padding: 0px;">${header}</p>
                    </div>
                    <canvas id="${graphId}" style="width:100%;max-width:600px;"></canvas>
                `;
                graphContainer.appendChild(graphDiv);

                const ctx = document.getElementById(graphId).getContext('2d');
                new Chart(ctx, {
                    type: graph_type,
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: graph_colors.length > 0 ? graph_colors : ['#70cac1', '#659d4e', '#208cc2'],
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: graph_legend === 'on' ? true : graph_legend === 'off' ? false : true, // Dynamic legend toggle
                            },
                            tooltip: {
                                callbacks: {
                                    label: (context) => {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const percentage = ((value / values.reduce((a, b) => a + b, 0)) * 100).toFixed(2);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            });
        } else {
            console.error('Graph container not found.');
        }
    }

    // List rendering ✅
    async render_lists(filter) {
        const sett_data = await this.orm.call('odi.home.page', 'get_sett_data', [filter]);
        const layout = parseInt(sett_data?.list_layout || 3, 10); // Ensure layout is a number
        const columnsClass = `col-lg-${12 / layout}`; // Dynamic Bootstrap grid class

        const data = await this.orm.call('odi.home.page', 'get_lists', [filter]);
        const listsContainer = document.getElementById('listsContainer');
        if (listsContainer) {
            listsContainer.innerHTML = '';

            data.forEach((list, index) => {
                const listId = `list_${index + 1}_${list.header.replace(/\s+/g, '_')}`;
                const { items, header, columns } = list;

                const listDiv = document.createElement('div');
                listDiv.classList.add('list-card', 'text-color', columnsClass); // Use dynamic column class
                listDiv.innerHTML = `
                    <div class="x-card-body pb-0">
                        <p class="stat-head" style="padding: 0px;">${header}</p>
                        <ul id="${listId}" style="list-style-type: none; padding: 0;">
                            <!-- Header Row -->
                            <li class="header-row" style="display: flex; justify-content: space-between;">
                                ${columns.map(col => `<span>${col}</span>`).join('')}
                            </li>
                            <!-- Data Rows -->
                            ${items.map(item => `
                                <li style="display: flex; justify-content: space-between;">
                                    ${columns.map(col => `<span>${item[col]}</span>`).join('')}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
                listsContainer.appendChild(listDiv);
            });
        } else {
            console.error('List container not found.');
        }
    }

    // Additional methods
    getIconClass(index) {
        const icons = [
            'fa-bar-chart',
            'fa-clock-o',
            'fa-book',
            'fa-money',
            'fa-money',
            'fa-bar-chart',
            'fa-clock-o',
            'fa-book',
        ];
        return icons[index - 1] || 'fa-bar-chart';
    }

    getCardClass() {
        const sizeMap = {
            '1': 'home-card-small',   // Small (S)
            '2': 'home-card-medium',  // Medium (M)
            '3': 'home-card-large',   // Large (L)
            '4': 'home-card-xl',      // Extra Large (XL)
        };
        const size = (this.state.oi_set.card || '2').toString(); // Ensure it's a string
        return sizeMap[size] || 'home-card-medium';
    }


    getFavButtonClass(style) {
        return `btn ${style}`;
    }

    btn_open_favourite(url, tab) {
        if (url) {
            window.open(url, tab || '_self');
        } else {
            console.warn("No URL provided for favourite link");
        }
    }

    btn_setting() {
        if (this.state.oi_bse.user_id) {
            this.action.doAction({
                name: _t("Setting"),
                type: 'ir.actions.act_window',
                res_model: 'odi.hp.setting',
                view_mode: 'list',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
            });
        } else {
            console.error("Session UID is undefined.");
        }
    }

    btn_kpi() {
        if (this.state.oi_bse.user_id) {
            this.action.doAction({
                name: _t("Config"),
                type: 'ir.actions.act_window',
                res_model: 'odi.hp.config',
                view_mode: 'list',
                views: [[false, 'list'], [false, 'form']],
                domain: [['company_id', '=', this.state.oi_bse.company_id.id]],
                target: 'current',
            });
        } else {
            console.error("Session UID is undefined.");
        }
    }

    handleCardClick(tile) {
        if (!this.state || !this.state.oi_usd) {
            console.error("this.state or this.state.oi_usd is undefined.");
            return;
        }

        const tileData = this.state.oi_usd;

        if (tileData[`${tile}_model`]) { // Fix: using tile instead of t${index}
            const action = {
                name: tileData[`${tile}_lab`] || "KPI Data",
                type: 'ir.actions.act_window',
                res_model: tileData[`${tile}_model`],
                view_mode: tileData[`${tile}_view_mode`],
                views: tileData[`${tile}_views`],
                domain: tileData[`${tile}_domain`],
                target: tileData[`${tile}_target`],
            };

            if (this.action && this.action.doAction) {
                this.action.doAction(action);
            } else {
                console.error("Action object is not available.");
            }
        } else {
            console.error(`No data found for tile ${tile}.`);
        }
    }

}

// Register the component
registry.category("actions").add("home_page", oHomePage);


