import React, { Component, Fragment } from 'react';
import {
    BrowserRouter as Router,
    Redirect,
    Switch,
    Route,
} from 'react-router-dom'
import { bindActionCreators } from "redux";
import { connect } from 'react-redux';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import { fetchPrinters } from './actions';
import Nav from './components/Nav';
import CamMain from './components/cam/CamMain';
import PrinterForm from './components/printer/PrinterForm';
import logo from './logo.svg';
import './App.css';

const theme = createMuiTheme();

class AppComponent extends Component {
    componentDidMount() {
        this.props.fetchPrinters();
    }

    render() {
        return (
                <MuiThemeProvider theme={theme}>
                    <Router>
                        <Nav>
                            <Switch>
                                <Route path="/cam" exact component={CamMain} />
                                <Route path="/printers/new" exact component={PrinterForm} />
                            </Switch>
                        </Nav>
                    </Router>
                </MuiThemeProvider>
        )
    }
}

const mapDispatchToProps = dispatch => {
    return bindActionCreators(
        {
            fetchPrinters,
        },
        dispatch
    );
};

export default connect(null, mapDispatchToProps)(AppComponent);