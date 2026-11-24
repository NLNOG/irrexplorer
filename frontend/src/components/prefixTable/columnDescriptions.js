// What each column of the prefix table shows, used in the header
// tooltips and in the explanation of the prefix table.
const columnDescriptions = {
    prefix: 'The prefix found in BGP, IRR or RPKI.',
    rir: 'The RIR that allocated/assigned this prefix.',
    bgp: 'The origin AS number(s) seen in the DFZ (the global BGP routing table) for this prefix.',
    rpki: 'The origin AS and maximum prefix length of each ROA for this prefix. ROAs for less specific prefixes are shown on their own rows, but also cover this prefix.',
    irr: 'The origin AS number(s) of route(6) objects for this prefix in this IRR database.',
    advice: 'Information, warnings and alerts about the BGP, IRR and RPKI status of this prefix.',
};

export default columnDescriptions;
