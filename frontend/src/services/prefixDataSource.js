import _ from 'lodash';

import api from "./api";

class PrefixDataSource {
    constructor(queryPrefix, onLeastSpecificFound) {
        this.queryPrefix = queryPrefix;
        this.onLeastSpecificFound = onLeastSpecificFound;
    }

    reset() {
        if (this.onLeastSpecificFound)
            this.onLeastSpecificFound(null);
        return {prefixesData: [], irrSourceColumns: [], hasLoaded: false};
    }

    async load() {
        this.reset();

        const prefixesData = await api.getPrefixesData(this.queryPrefix);
        const irrSourceColumns = this.gatherIrrSourceColumns(prefixesData);
        this.notifyLeastSpecificFound(prefixesData);
        return {prefixesData, irrSourceColumns, hasLoaded: true};
    }

    gatherIrrSourceColumns(prefixesData) {
        // Other than a few fixed columns, there are columns for each source
        // found for at least one prefix. This method therefore finds the set
        // of all IRR sources, used to display the columns.
        let irrSources = [];
        for (const prefixData of prefixesData) {
            const sourcesForPrefix = Object.keys(prefixData.irrRoutes);
            irrSources.push(...sourcesForPrefix);
        }
        return _.uniq(irrSources).sort();
    }

    notifyLeastSpecificFound(prefixesData) {
        // The prefix query page first renders directly overlapping prefixes,
        // but if applicable, then also renders all overlaps of the least specific
        // overlapping prefix found. This method detects finds the least specific
        // prefix from the API results, and if it is shorter than the query,
        // calls a callback.
        if (!prefixesData.length || !this.onLeastSpecificFound)
            return
        const queryPrefixLength = this.queryPrefix.split('/')[1];
        const allPrefixes = prefixesData.map(({prefix}) => {
            const [ip, len] = prefix.split('/')
            return {ip, len};
        });
        allPrefixes.sort((a, b) => a.len > b.len);
        const leastSpecific = allPrefixes[0];
        if (!queryPrefixLength || leastSpecific.len < queryPrefixLength)
            this.onLeastSpecificFound(allPrefixes[0].ip + '/' + allPrefixes[0].len);
    }
}

export default PrefixDataSource;
