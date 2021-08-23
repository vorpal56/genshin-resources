import Head from 'next/head';
import Image from 'next/image';
import React from 'react';
import Layout from '../components/Layout/Layout';

export default function Home() {
  return <Example />;
}

class Example extends React.Component {
  constructor(props: any) {
    super(props);
  }
  render() {
    return <Layout>This is from index</Layout>;
  }
}
