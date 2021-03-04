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
        hasLoadedSets: false,
        setData: {irrsSeen: [], setsPerIrr: []},
    };

    async componentDidMount() {
        await this.loadPrefixesData();
        await this.loadSetData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.queryASN !== this.props.queryASN) {
            await this.loadPrefixesData();
            await this.loadSetData();
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

    async loadSetData() {
        this.setState({
            hasLoadedSets: false,
            setData: {irrsSeen: [], setsPerIrr: []},
        });
        const response = await api.getSetMemberOf(this.props.queryASN);
        console.log(response);
        this.setState({
            hasLoadedSets: true,
            setData: response,
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
                    hasLoaded={this.state.hasLoadedPrefixes}
                />
                <h2 className="h3 mt-4">
                    Other prefixes overlapping with prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={this.state.overlapPrefixes}
                    hasLoaded={this.state.hasLoadedPrefixes}
                />
                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <AsSetTable
                    irrsSeen={this.state.setData.irrsSeen}
                    setsPerIrr={this.state.setData.setsPerIrr}
                    hasLoaded={this.state.hasLoadedPrefixes}
                />

            </>
        );
    }
}

ASNQuery.propTypes = {
    queryASN: PropTypes.string.isRequired,
};

export default ASNQuery;
