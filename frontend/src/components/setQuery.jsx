import React, {Component} from 'react';
import PropTypes from 'prop-types';
import SetIncludedTable from "./common/setIncludedTable";
import SetExpansionTable from "./setExpansionTable/setExpansionTable";

class setQuery extends Component {
    render() {
        const {query, queryCategory} = this.props;
        return (
            <>
                <h1>Report for {queryCategory} {query}</h1>

                <h2 className="h3 mt-4">
                    Expands to:
                </h2>
                <hr/>
                <SetExpansionTable query={query} objectClass={queryCategory}/>
                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <SetIncludedTable query={query} objectClass={queryCategory} />
            </>
        );
    }
}

setQuery.propTypes = {
    query: PropTypes.string.isRequired,
    queryCategory: PropTypes.string.isRequired,
};

export default setQuery;
