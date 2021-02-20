import React, {useState} from 'react';
import {navigate} from "@reach/router";

function SearchForm() {
    const [search, setSearch] = useState('');

    const handleSearchSubmit = (event) => {
        event.preventDefault();
        if (!search) return;
        navigate(`/search/${search}`);
    }

    const handleSearchChange = ({currentTarget: input}) => {
        setSearch(input.value);
    }
    return (
        <form className="row" onSubmit={handleSearchSubmit}>
            <div className="col-sm-10">
                <label className="visually-hidden" htmlFor="search">Search input</label>
                <div className="input-group">
                    <input type="text" className="form-control form-control-lg" id="search"
                           placeholder="Prefix, IP, ASN or AS-set" onChange={handleSearchChange}/>
                </div>
            </div>

            <div className="col-sm-2">
                <button type="submit" className="btn btn-success btn-lg" disabled={!search}>Search
                </button>
            </div>
        </form>
    );
}

export default SearchForm;
