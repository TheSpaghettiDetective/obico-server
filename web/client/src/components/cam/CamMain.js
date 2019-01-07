import React, { Component } from 'react';
import { withStyles } from '@material-ui/core/styles';
import _ from 'lodash';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Gauge from 'react-svg-gauge';

const styles = theme => ({
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  camImg: {
    width: '100%',
  }
});


class CamComponent extends Component {
  state = {detection: null}

  componentDidMount() {
    this.interval = setInterval(() => {
      fetch('/api/detections')
      .then( resp => resp.json() )
      .then( detection => {
        this.setState({detection})
      })
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    const { classes } = this.props;
    if (!this.state.detection) {
      return <div />;
    }

    const {input_img_url, score} = this.state.detection;

    return (
      <div>
        <Grid container spacing={24} justify='center'>
          <Grid item xs={12} md={6} lg={4}>
            <Paper className={classes.paper}>
            <Gauge value={(score*100).toFixed()} width={200} height={160} label="Tangle Index" />
              <img src={input_img_url} className={classes.camImg} />
            </Paper>
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default withStyles(styles)(CamComponent);
