import React, {Component} from 'react';

import QueryForm from "./common/queryForm";
import PrefixTable from "./common/prefixTable";

import logo from "../logo.png";
import {Link, navigate} from "@reach/router";
import api from "../services/api";
import PrefixQuery from "./prefixQuery";

class Query extends Component {
    state = {cleanQuery: ''}

    async componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps === this.props) return;
        await this.cleanQuery();
    }

    async componentDidMount() {
        await this.cleanQuery();
    }

    async cleanQuery() {
        const cleanResult = await api.cleanQuery(this.queryInput());
        if (!cleanResult) {
            await navigate('/');
        } else if (cleanResult.category !== this.props.category) {
            await navigate(`/${cleanResult.category}/${cleanResult.cleanedValue}`);
        } else {
            this.setState({cleanQuery: cleanResult.cleanedValue})
            document.title = 'IRR explorer: ' + this.state.cleanQuery;
        }
    }

    queryInput() {
        return this.props.query
            ? this.props.query
            : this.props.query1 + '/' + this.props.query2;
    }

    render() {
        return (
            <div className="container">
                <div className="row d-flex align-items-center mb-5">
                    <div className="col-lg-1">
                        <Link to="/">
                            <img className="logo-small" src={logo} alt="IRR explorer"/>
                        </Link>
                    </div>
                    <div className="col-lg-5 offset-lg-1">
                        <QueryForm/>
                    </div>
                </div>
                {
                    this.state.cleanQuery
                    && this.props.category === 'prefix'
                    && <PrefixQuery queryPrefix={this.state.cleanQuery}/>
                }
            </div>
        );
    }
}

export default Query;
