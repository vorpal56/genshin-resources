import styles from './Footer.module.scss';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  return (
    <footer className={styles.footer}>
      <div className='container'>
        <div className={styles.footerName}>{currentYear} © Vorpal56</div>
        <div className={styles.footerLinks}>
          <a className={styles.footerLink} href='https://github.com/vorpal56' target='_blank'>
            <img className={styles.footerImage} src='/images/icons/common/github.png' />
          </a>
        </div>
        <div className={styles.credits}>
          <span>
            League Theory Crafter isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone
            officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or
            registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
          </span>
        </div>
        <div className={styles.credits}>
          <span>
            Big thanks to the{' '}
            <a href='https://leagueoflegends.fandom.com/wiki/League_of_Legends_Wiki'>League of Legends Wiki</a> and the team at{' '}
            <a href='https://github.com/meraki-analytics'>Meraki Analytics</a> for providing free and available data used in
            this application.
          </span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
