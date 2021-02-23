import React, {Component} from 'react';
import PropTypes from 'prop-types';

import QueryForm from "./common/queryForm";
import PrefixTable from "./common/prefixTable";

import logo from "../logo.png";
import {Link, navigate} from "@reach/router";
import api from "../services/api";

class PrefixQuery extends Component {
    render() {
        return (
            <>
                <h1>Prefix: {this.props.queryPrefix}</h1>
                <PrefixTable queryPrefix={this.props.queryPrefix}/>
            </>
        );
    }
}

PrefixQuery.propTypes = {
    queryPrefix: PropTypes.string.isRequired,
};

export default PrefixQuery;
