import {FC} from 'react';
import Footer from '../Footer/Footer';
import styles from './Layout.module.scss';

interface Props {
  children: any;
}

const Layout: FC<Props> = ({children}) => (
  <div className={styles.coreContainer}>
    <div className='container'>{children}</div>
    <div className={styles.footerContainer}>
      <Footer />
    </div>
  </div>
);

export default Layout;
