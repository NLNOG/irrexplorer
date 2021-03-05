import React, {Component} from 'react';
import PropTypes from 'prop-types';
import AsSetIncludedTable from "./common/asSetIncludedTable";
import AsSetExpansionTable from "./common/asSetExpansionTable";

class AsSetQuery extends Component {
    render() {
        const {query} = this.props;
        return (
            <>
                <h1>Report for AS-set {query}</h1>

                <h2 className="h3 mt-4">
                    Expands to:
                </h2>
                <hr/>
                <AsSetExpansionTable query={this.props.query}/>
                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <AsSetIncludedTable query={this.props.query}/>
            </>
        );
    }
}

AsSetQuery.propTypes = {
    query: PropTypes.string.isRequired,
};

export default AsSetQuery;
