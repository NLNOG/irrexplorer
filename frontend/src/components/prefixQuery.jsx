import React, {Component} from 'react';
import PropTypes from 'prop-types';
import PrefixTable from "./common/prefixTable";
import PrefixTableExplanation from "./common/prefixTableExplanation";

class PrefixQuery extends Component {
    state = {leastSpecificPrefix: null};

    handleLeastSpecificFound = (prefix) => {
        this.setState({leastSpecificPrefix: prefix});
    }

    render() {
        const {queryPrefix} = this.props;
        const {leastSpecificPrefix} = this.state;
        return (
            <>
                <h1>Report for prefix {queryPrefix}</h1>
                <PrefixTableExplanation />
                <h2 className="h3 mt-4">
                    Directly overlapping prefixes of {queryPrefix}
                </h2>
                <hr/>
                <PrefixTable
                    queryType="prefix"
                    query={queryPrefix}
                    onLeastSpecificFound={this.handleLeastSpecificFound}
                />

                {leastSpecificPrefix && <>
                    <h2 className="h3">
                        All overlaps of least specific match {leastSpecificPrefix}
                    </h2>
                    <hr/>
                    <PrefixTable
                        queryType="prefix"
                        query={leastSpecificPrefix}
                    />
                </>}
            </>
        );
    }
}

PrefixQuery.propTypes = {
    queryPrefix: PropTypes.string.isRequired,
};

export default PrefixQuery;
