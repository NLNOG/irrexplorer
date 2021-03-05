import React, {Component} from 'react';
import PropTypes from 'prop-types';

import PrefixTableExplanation from "./common/prefixTableExplanation";
import PrefixTable from "./common/prefixTable";
import api from "../services/api";
import AsSetTable from "./common/asSetTable";

class AsSetQuery extends Component {
    // state = {
    //     hasLoadedPrefixes: false,
    //     directOriginPrefixes: [],
    //     overlapPrefixes: [],
    // };
    //
    // async componentDidMount() {
    //     await this.loadPrefixesData();
    // }
    //
    // async componentDidUpdate(prevProps) {
    //     if (prevProps.queryASN !== this.props.queryASN) {
    //         await this.loadPrefixesData();
    //     }
    // }
    //
    // async loadPrefixesData() {
    //     this.setState({
    //         hasLoadedPrefixes: false,
    //         directOriginPrefixes: [],
    //         overlapPrefixes: [],
    //     });
    //     const response = await api.getPrefixesForASN(this.props.queryASN);
    //     this.setState({
    //         hasLoadedPrefixes: true,
    //         directOriginPrefixes: response.directOrigin,
    //         overlapPrefixes: response.overlaps,
    //     });
    // }

    render() {
        const {query} = this.props;
        return (
            <>
                <h1>Report for AS-set {query}</h1>

                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <AsSetTable query={this.props.query}/>
            </>
        );
    }
}

AsSetQuery.propTypes = {
    query: PropTypes.string.isRequired,
};

export default AsSetQuery;
