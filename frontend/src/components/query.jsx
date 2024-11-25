import React, {Component} from 'react';

import QueryForm from "./common/queryForm";

import logo from "../logo.png";
import {Link, navigate} from "@reach/router";
import api from "../services/api";
import PrefixQuery from "./prefixQuery";
import ASNQuery from "./asnQuery";
import setQuery from "./setQuery";

class Query extends Component {
    state = {cleanQuery: '', queryCategory: '', reducedColour: false, filterWarningError: false};

    async componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps === this.props) return;
        await this.cleanQuery();
    }

    async componentDidMount() {
        await this.cleanQuery();
    }

    async cleanQuery() {
        const cleanResult = await api.cleanQuery(this.queryInput());
        if (cleanResult.error) {
            await navigate('/');
        } else if (cleanResult.category !== this.props.category) {
            await navigate(`/${cleanResult.category}/${cleanResult.cleanedValue}`, {replace: true});
        } else {
            this.setState({cleanQuery: cleanResult.cleanedValue, queryCategory: cleanResult.category})
            document.title = 'IRR explorer: ' + this.state.cleanQuery;
        }
    }

    queryInput() {
        return this.props.query
            ? this.props.query
            : this.props.query1 + '/' + this.props.query2;
    }

    contentClass() {
        switch (this.state.queryCategory) {
            case 'prefix':
                return PrefixQuery;
            case 'asn':
                return ASNQuery;
            case 'as-set':
            case 'route-set':
                return setQuery;
            default:
                return undefined;
        }
    }

    handleReducedColourChange = ({currentTarget: input}) => {
        this.setState({reducedColour: input.checked});
    }
    handleFilterWarningErrorChange = ({currentTarget: input}) => {
        this.setState({filterWarningError: input.checked});
    }

    render() {
        const ContentClass = this.contentClass();
        return (
            <div className="m-2 m-lg-4">
                <div className="row d-flex align-items-center mb-5">
                    <div className="col-lg-1">
                        <Link to="/">
                            <img className="logo-small" src={logo} alt="IRR explorer"/>
                        </Link>
                    </div>
                    <div className="col-lg-5 offset-lg-1">
                        <QueryForm/>
                    </div>
                    <form className="text-end">
                        <input
                            type="checkbox"
                            id="reducedColour"
                            className="me-2"
                            checked={this.state.reducedColour}
                            onChange={this.handleReducedColourChange}
                        />
                        <label htmlFor="reducedColour" className="me-4">Reduced colour mode</label>
                        <input
                            type="checkbox"
                            id="filterWarningError"
                            className="me-2"
                            checked={this.state.filterWarningError}
                            onChange={this.handleFilterWarningErrorChange}
                        />
                        <label htmlFor="filterWarningError">Show only error/warning</label>
                    </form>
                </div>
                {
                    this.state.cleanQuery
                    && <ContentClass query={this.state.cleanQuery} reducedColour={this.state.reducedColour} filterWarningError={this.state.filterWarningError} queryCategory={this.state.queryCategory} />
                }
            </div>
        );
    }
}

export default Query;
