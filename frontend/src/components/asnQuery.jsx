import React, {Component} from 'react';
import PropTypes from 'prop-types';

import PrefixTableExplanation from "./common/prefixTableExplanation";
import PrefixTable from "./common/prefixTable";
import api from "../services/api";
import AsSetTable from "./common/asSetTable";

class ASNQuery extends Component {
    state = {
        hasLoadedPrefixes: false,
        directOriginPrefixes: [],
        overlapPrefixes: [],
    };

    async componentDidMount() {
        await this.loadPrefixesData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.queryASN !== this.props.queryASN) {
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        this.setState({
            hasLoadedPrefixes: false,
            directOriginPrefixes: [],
            overlapPrefixes: [],
        });
        const response = await api.getPrefixesForASN(this.props.queryASN);
        this.setState({
            hasLoadedPrefixes: true,
            directOriginPrefixes: response.directOrigin,
            overlapPrefixes: response.overlaps,
        });
    }

    render() {
        const {queryASN} = this.props;
        const {overlapPrefixes, hasLoadedPrefixes, directOriginPrefixes} = this.state;
        return (
            <>
                <h1>Report for ASN {queryASN}</h1>
                <PrefixTableExplanation/>
                <h2 className="h3 mt-4">
                    Prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={directOriginPrefixes}
                    hasLoaded={hasLoadedPrefixes}
                />
                <h2 className="h3 mt-4">
                    Other prefixes overlapping with prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={overlapPrefixes}
                    hasLoaded={hasLoadedPrefixes}
                />
                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <AsSetTable query={this.props.queryASN}/>
            </>
        );
    }
}

ASNQuery.propTypes = {
    queryASN: PropTypes.string.isRequired,
};

export default ASNQuery;
