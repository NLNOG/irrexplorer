import React, {useState} from 'react';
import {navigate} from "@reach/router";

import api from "../../services/api";

function QueryForm() {
    const [search, setSearch] = useState('');
    const [isValid, setIsValid] = useState(true);

    const handleSearchSubmit = async (event) => {
        event.preventDefault();
        if (!search) return;

        const cleanResult = await api.cleanQuery(search);
        if (!cleanResult) {
            setIsValid(false);
        } else {
            await navigate(`/${cleanResult.category}/${cleanResult.cleanedValue}`, {replace: true});
        }
    }

    const handleSearchChange = ({currentTarget: input}) => {
        setIsValid(true);
        setSearch(input.value);
    }
    let inputClasses = "form-control form-control-lg ";
    if (!isValid)
        inputClasses += "is-invalid";

    return (
        <form className="row" onSubmit={handleSearchSubmit}>
            <div className="col-sm-10">
                <label className="visually-hidden" htmlFor="search">Search input</label>
                <div className="input-group has-validation">
                    <input
                        type="text"
                        id="search"
                        placeholder="Prefix, IP, ASN or AS-set"
                        onChange={handleSearchChange}
                        className={inputClasses}
                    />
                    <div className="invalid-feedback">
                        This is not a valid prefix, IP, ASN or AS-set.
                    </div>
                </div>
            </div>

            <div className="col-sm-2">
                <button type="submit" className="btn btn-success btn-lg" disabled={!search}>Search
                </button>
            </div>
        </form>
    );
}

export default QueryForm;
