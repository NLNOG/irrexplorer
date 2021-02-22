import React, {Component} from 'react';

import SearchForm from "./common/searchForm";
import PrefixTable from "./prefixTable";

import logo from "../logo.png";

class Search extends Component {
    state = {prefixData: [], irrSourceColumns: []}

    searchInput() {
        return this.props.search
            ? this.props.search
            : this.props.search1 + '/' + this.props.search2;
    }

    render() {
        return (
            <div className="container">
                <div className="row d-flex align-items-center mb-5">
                    <div className="col-lg-1">
                        <img className="logo-small" src={logo} alt="IRR explorer"/>
                    </div>
                    <div className="col-lg-5 offset-lg-1">
                        <SearchForm/>
                    </div>
                </div>
                <h1>Query: {this.searchInput()}</h1>
                <PrefixTable searchPrefix={this.searchInput()}/>
            </div>
        );
    }
}

export default Search;
