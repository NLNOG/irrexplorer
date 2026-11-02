import React from 'react';
import {useNavigate, useParams} from "react-router";

// Route params and navigate as props, for the class components.
function withRouter(Component) {
    return function WithRouter(props) {
        const params = useParams();
        const navigate = useNavigate();
        return <Component {...props} {...params} navigate={navigate}/>;
    };
}

export default withRouter;
