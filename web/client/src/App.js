import React, { Component, Fragment } from 'react';
import {
    BrowserRouter as Router,
    Redirect,
    Switch,
    Route,
} from 'react-router-dom'
import { Provider } from 'react-redux'
import { createStore, applyMiddleware, combineReducers } from "redux";
import { reducer as form } from 'redux-form';
import thunk from "redux-thunk";
import logger from "redux-logger";
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import CssBaseline from "@material-ui/core/CssBaseline";

import reducers from "./reducers";
import Nav from './components/Nav';
import CamMain from './components/cam/CamMain';
import logo from './logo.svg';
import './App.css';

const theme = createMuiTheme();

const initState = {}
const store = createStore(combineReducers({...reducers, form}), initState, applyMiddleware(thunk, logger));

class App extends Component {
    render() {
        return (
            <Provider store={store}>
            <MuiThemeProvider theme={theme}>
                <div style={{display: 'flex'}}>
                    <CssBaseline />
                    <Router>
                        <Fragment>
                            <Nav />
                            <div style={{height: '100vh', padding: '24px', overflow: 'auto', flexGrow: '1'}}>
                            <Switch>
                                <Route path="/cam" exact component={CamMain} />
                            </Switch>
                            </div>
                        </Fragment>
                    </Router>
                </div>
            </MuiThemeProvider>
            </Provider>
        )
    }
}

export default App;
