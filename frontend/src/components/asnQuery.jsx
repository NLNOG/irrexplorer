import React, {Component} from 'react';
import PropTypes from 'prop-types';
import PrefixTable from "./common/prefixTable";
import PrefixTableExplanation from "./common/prefixTableExplanation";

class ASNQuery extends Component {


    render() {
        const {queryASN} = this.props;
        return (
            <>
                <h1>Report for ASN {queryASN}</h1>
                <PrefixTableExplanation />
                <h2 className="h3 mt-4">
                    Prefixes originated by {queryASN}
                </h2>
                <hr/>
                <PrefixTable
                    queryType="asn"
                    query={queryASN}
                />

            </>
        );
    }
}

ASNQuery.propTypes = {
    queryASN: PropTypes.string.isRequired,
};

export default ASNQuery;
