import React, {Component} from 'react';
import PropTypes from 'prop-types';
import PrefixTable from "./common/prefixTable";

class PrefixQuery extends Component {
    state = {leastSpecificPrefix: null};

    handleLeastSpecificFound = (prefix) => {
        this.setState({leastSpecificPrefix: prefix});
    }

    render() {
        return (
            <>
                <h1 className="mb-5">Report for prefix {this.props.queryPrefix}</h1>
                <h2 className="h3">
                    Directly overlapping prefixes of {this.props.queryPrefix}
                </h2>
                <hr/>
                <PrefixTable
                    queryPrefix={this.props.queryPrefix}
                    onLeastSpecificFound={this.handleLeastSpecificFound}
                />

                {this.state.leastSpecificPrefix && <>
                    <h2 className="h3">
                        All overlaps of least specific match {this.state.leastSpecificPrefix}
                    </h2>
                    <hr/>
                    <PrefixTable
                        queryPrefix={this.state.leastSpecificPrefix}
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
