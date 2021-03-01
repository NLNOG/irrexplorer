import _ from 'lodash';

import api from "./api";

export class PrefixDataSource {
    constructor(queryType, query, onLeastSpecificFound) {
        this.queryType = queryType;
        this.query = query;
        this.onLeastSpecificFound = onLeastSpecificFound;
    }

    reset() {
        if (this.onLeastSpecificFound)
            this.onLeastSpecificFound(null);
        return {prefixesData: [], irrSourceColumns: [], hasLoaded: false};
    }

    async load() {
        this.reset();

        let prefixesData = undefined;
        if(this.queryType === 'prefix')
            prefixesData = await api.getPrefixesForPrefix(this.query);
        if(this.queryType === 'asn')
            prefixesData = await api.getPrefixesForASN(this.query);
        const irrSourceColumns = this.gatherIrrSourceColumns(prefixesData);
        this.notifyLeastSpecificFound(prefixesData);
        const sortedPrefixesData = sortPrefixesDataBy(prefixesData,'prefix');
        return {prefixesData: sortedPrefixesData, irrSourceColumns, hasLoaded: true};
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
        if (!prefixesData.length || this.queryType !== 'prefix' || !this.onLeastSpecificFound)
            return
        const queryPrefixLength = parseInt(this.query.split('/')[1], 10);
        const allPrefixes = prefixesData.map(({prefix}) => {
            const [ip, len] = prefix.split('/')
            return {ip, len: parseInt(len, 10)};
        });
        allPrefixes.sort((a, b) => a.len > b.len);
        const leastSpecific = allPrefixes[0];
        if (!queryPrefixLength || leastSpecific.len < queryPrefixLength)
            this.onLeastSpecificFound(allPrefixes[0].ip + '/' + allPrefixes[0].len);
    }

}

export function sortPrefixesDataBy(prefixesData, key, order = 'asc') {
    if (key === 'prefix') key = 'prefixExploded';
    if (key === 'bgpOrigins') key = 'bgpOrigins.0';
    if (key === 'rpkiRoutes') key = 'rpkiRoutes.0.asn';
    if (key.startsWith('irrRoutes')) key += '.0.asn';
    if (key === 'messages') key = 'goodnessOverall';
    return _.orderBy(prefixesData, [key], [order]);
}
