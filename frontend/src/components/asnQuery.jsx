import React, {Component} from 'react';
import PropTypes from 'prop-types';

import PrefixTableExplanation from "./common/prefixTableExplanation";
import PrefixTable from "./common/prefixTable";
import api from "../services/api";

class ASNQuery extends Component {
    state = {
        hasLoaded: false,
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
            hasLoaded: false,
            directOriginPrefixes: [],
            overlapPrefixes: [],
        });
        const response = await api.getPrefixesForASN(this.props.queryASN);
        this.setState({
            hasLoaded: true,
            directOriginPrefixes: response.directOrigin,
            overlapPrefixes: response.overlaps,
        });
    }

    render() {
        const {queryASN} = this.props;
        return (
            <>
                <h1>Report for ASN {queryASN}</h1>
                <PrefixTableExplanation/>
                <h2 className="h3 mt-4">
                    Prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={this.state.directOriginPrefixes}
                    hasLoaded={this.state.hasLoaded}
                />
                <h2 className="h3 mt-4">
                    Other prefixes overlapping with prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={this.state.overlapPrefixes}
                    hasLoaded={this.state.hasLoaded}
                />

            </>
        );
    }
}

ASNQuery.propTypes = {
    queryASN: PropTypes.string.isRequired,
};

export default ASNQuery;
